# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
#                Aurélien Calonne <aurel@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from App.Extensions import getBrain
from Acquisition import aq_base
from lxml import etree
from zLOG import LOG
from base64 import b16encode

SEPARATOR = '\n'

TioSafeBrain = getBrain('TioSafeBrain', 'TioSafeBrain', reload=1)
TransactionBrain = getBrain('TioSafeBrain', 'Transaction', reload=1)

class MagentoBrain(TioSafeBrain):

  def _setArrowTag(self, document=None, xml=None, source_tag='source',
      destination_tag='destination', category=''):
    """ This method build the XML of the arrow. """
    # only work on the data of the document and not on its parent's data
    document = aq_base(document)
    sync_list = self.getTioSafeSynchronizationObjectList(object_type="Person")

    # create the arrow tag and set if exist source and destination
    arrow = etree.SubElement(xml, 'arrow', type=category)
    arrow_list = [(source_tag, 'source'), (destination_tag, 'destination')]
    for prop, tag in arrow_list:
      if getattr(document, prop, None) is not None:
        movement = etree.SubElement(arrow, tag)
        object_id = getattr(document, prop)
        if object_id != 'default_node':
          for sync in sync_list:
            try:
              #brain_node = sync.getObjectFromId(object_id)
              #node_gid = brain_node.getGid()
              node_gid = object_id
              break
            except (ValueError, AttributeError):
              # This is not a document, might be a category, or the gid previously built
              # pass it anyway in xml
              node_gid = None

          if node_gid is None:
            node_gid = self.getDefaultUnknownNodeGID()
          movement.text = node_gid
        else:
          movement.text = self.getDefaultOrganisationGID()


class MagentoTransaction(MagentoBrain):
  """
    This class allows to build the TioSafe XML of a Sale Order and to sync.
  """
  __allow_access_to_unprotected_subobjects__ = 1

  def __init__(self, object_type, context, **kw):
    self.source = "default_node"
    self.source_ownership = "default_node"
    self.source_decision = "default_node"
    self.source_administration = "default_node"
    MagentoBrain.__init__(self, object_type, context, **kw)

  def getVATCategory(self, vat_value):
    """
    This returns the VAT category according to the value set
    """
    # XXX-AUREL this must be cached for performance reason
    vat_dict = {}
    trade_condition = self.getIntegrationSite().getDefaultSourceTradeValue()

    while len(trade_condition.contentValues(portal_type="Trade Model Line")) == 0:
      # Must find a better way to browse specialised objects
      trade_condition = trade_condition.getSpecialiseValue()
      if trade_condition is None or trade_condition.getPortalType() == "Business Process":
        return None

    for vat_line in trade_condition.contentValues(portal_type="Trade Model Line"):
      #LOG("browsing line %s" %(vat_line.getPath(), 300, "%s" %(vat_line.getBaseApplicationList(),)))
      for app in vat_line.getBaseApplicationList():
        if "base_amount/trade/base/taxable/vat/" in app:
          vat_dict["%.2f" %(vat_line.getPrice()*100.)] = app.split('/')[-1]
    LOG("vat_dict is %s" %(vat_dict), 300, "")
    return vat_dict["%.2f" %(float(vat_value))]

  def _setPaymentMode(self, txn):
    """
    Define the payment mode of a transaction
    This must be the category payment_mode/XXX
    """
    if getattr(self, 'payment_mode', None) is not None:
      payment_mapping = self.getIntegrationSite().getCategoryFromMapping(
        category='Payment Mode/%s' % getattr(self, 'payment_mode'),
        create_mapping=True,
        create_mapping_line=True,
        )
      element = etree.SubElement(txn, 'payment_mode')
      element.text = payment_mapping.split('/', 1)[-1]

  def _asXML(self):
    transaction_type = self.context.getDestinationObjectType()
    transaction = etree.Element('transaction', type=transaction_type)
    tiosafe_sync_list = self.getTioSafeSynchronizationObjectList(object_type='Product')
    erp5_sync_list = self.getERP5SynchronizationObjectList(object_type='Product')
    integration_site = self.getIntegrationSite()

    # marker for checking property existency
    MARKER = object()

    # list of possible tags for a sale order
    tag_list = (
        'title', 'start_date', 'stop_date', 'reference', 'currency',
    )
    self._setTagList(self, transaction, tag_list)
    self._setTagList(self, transaction, ['category', ], SEPARATOR)
    # set arrow list
    try:
      self._setPaymentMode(transaction)
      self._setArrowTagList(self, transaction)
    except ValueError:
      # A mapping must be missing
      return None

    # order the movement list
    movement_list = []

    # build a list of 2-tuple
    # the first key contains the sort element
    # the second part of the tuple contains a dict which contains all the data
    # of the transaction line
    method_id = self.getPortalType().replace(' ', '')
    portal_type = self.getPortalType().replace(' ', '_').lower()
    line_type_list = ['', 'Delivery', 'Discount', ]

    module_id = "%s_module" %(portal_type)
    module = getattr(integration_site, module_id)

    for line_type in line_type_list:
      getter_line_method = getattr(
          module,
          'get%s%sLineList' % (line_type, method_id),
          MARKER,
      )
      if getter_line_method is not MARKER:
        # browse each transaction lines, build the sort element and set data
        parameter_kw = {'%s_id' % portal_type: str(self.getId()), }
        for line in getter_line_method(**parameter_kw):
          key_list = ['title', 'resource', 'reference', 'quantity', 'price']
          value_list = [getattr(line, x, '') for x in key_list]
          movement_dict = {'context': line,}
          # set to None the '' value of the list
          for k, v in zip(key_list, value_list):
            movement_dict[k] = v or None

          # set the VAT value
          movement_dict['VAT'] = self.getVATCategory(getattr(line, 'vat', None))

          # the following boolean var allows to check if variation will be sync
          variation_sync = True

          # retrieve the resource and the gid in the line
          if not line_type:
            # work on transaction lines
            for tiosafe_sync in tiosafe_sync_list:
              try:
                # FIXME: Is it always product_id give as parameter ?
                brain_node = tiosafe_sync.getObjectFromId(line.product_id)
                resource_gid = brain_node.getGid()
                break
              except (ValueError, AttributeError):
                resource_gid = None

            if resource_gid is None:
              resource_gid = self.getDefaultUnknownResourceGID()

            for erp5_sync in erp5_sync_list:
              try:
                resource = erp5_sync.getDocumentFromGid(b16encode(resource_gid))
                break
              except (ValueError, AttributeError):
                resource = None
                # do not sync variations with the Unknown product
                variation_sync = False
          else:
            # do not sync variations with delivery or discount
            variation_sync = False
            # work on delivery and discount transaction lines
            resource_gid = resource_id = line.resource
            try:
              brain_node = tiosafe_sync.getObjectFromId(resource_id)
              resource_gid = brain_node.getGid()
            except (ValueError, AttributeError):
              # case of default delivery/discount
              if not 'Service' in resource_id:
                resource_gid = ' Unknown'
              LOG(
                  'Transaction, getting resource failed',
                  300,
                  'resource_id = %s, remains %s' % (resource_id, resource_gid),
              )
              pass
            # through the type render the delivery or the discount
            if line_type == 'Discount':
              resource = integration_site.getSourceCarrierValue()
            elif line_type == 'Delivery':
              resource = integration_site.getDestinationCarrierValue()
            else:
              raise ValueError, 'Try to work on "%s" which is an invalid type.' % line_type
          # after the work on the line set the resource value which will be
          # render in the xml
          movement_dict['resource'] = resource_gid

          # browse line variations and set them to a list
          getter_line_category_method = getattr(
              module,
              'get%sLineCategoryList' % method_id,
              MARKER,
          )
          category_value_list = [getattr(line, 'category', ''), ]
          # FIXME: variation are sync only on line with a product ?
          # else don't sync variations for delivery, discount and Unknown prodcut
          if variation_sync and \
              getter_line_category_method is not MARKER:
            parameter_kw = {
                '%s_id' % portal_type: str(self.getId()),
                '%s_line_id' % portal_type: str(line.getId()),
            }
            for brain in getter_line_category_method(**parameter_kw):
              try:
                category_value_list.append(
                    integration_site.getCategoryFromMapping(
                        brain.category,
                        resource,
                    )
                )
              except ValueError:
                return None

          # sort categories, build the sort key and set categoires in the dict
          if len(category_value_list):
            category_value_list.sort()
            movement_dict['category'] = category_value_list
          # build the element which allows to sort
          movement_list.append(movement_dict)

    # Sort the movement list for fix point
    def cmp_resource(a,b):
      a_str = "%s %s %s" %(a['resource'], a['title'], ' '.join(a['category']))
      b_str = "%s %s %s" %(b['resource'], b['title'], ' '.join(b['category']))
      return cmp(a_str, b_str)

    movement_list.sort(cmp=cmp_resource)

    # the second part build the XML of the transaction
    # browse the ordered movement list and build the movement list as a result
    # the xml through of the line data in the dict
    for movement_dict in movement_list:
      movement = etree.SubElement(transaction, 'movement')
      # set arrow list on the movement
      self._setArrowTagList(movement_dict['context'], movement)
      # if exist the following tags in the line dict, add them in the xml
      tag_list = ('resource', 'title', 'reference', 'quantity', 'price', 'VAT')
      for tag in tag_list:
        if tag in movement_dict:
          element = etree.SubElement(movement, tag)
          element.text = movement_dict[tag]
      # add the categories to the movement
      for category_value in movement_dict['category']:
        if len(category_value):
          category = etree.SubElement(movement, 'category')
          category.text = category_value

    xml = etree.tostring(transaction, pretty_print=True, encoding='utf-8')
    LOG("Transactions asXML returns : %s" % (xml, ), 300, "")
    return xml
