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
from zLOG import LOG, ERROR
from base64 import b16encode, b16decode

SEPARATOR = '\n'

NodeBrain = getBrain('TioSafeBrain', 'Node', reload=1)
TransactionBrain = getBrain('TioSafeBrain', 'Transaction', reload=1)

class OxatisNode(NodeBrain):

  def __init__(self, *args, **kw):
    NodeBrain.__init__(self, *args, **kw)
    # country property is used in gid computation of organisation
    # transform it to category as soon as possible
    if getattr(self, 'country', None) is not None:
      try:
        self.country = self.getIntegrationSite().getCategoryFromMapping(
          category = 'Country/%s' % self.country, create_mapping=True,
          create_mapping_line=True,
          ).split('/', 1)[-1]
      except ValueError, msg:
        LOG("OxatisBrain.OxatisNode.__init__", ERROR, "Getting category for %s raise with msg = %s" %(value, msg))
        self.country = ""


  def _generateCoordinatesXML(self, node):
    """ Generates xml for phones, faxes and email """

    self._setTagList(self, node, ['email',])

    # Address always ordered billing first then shipping if exists
    address_tag_list = ['street', 'zip', 'city', 'country']
    phone_tag_list = ['phone', 'cellphone', 'fax']
    for tag in ['billing', 'shipping']:
      for phone_tag in phone_tag_list:
        value = getattr(self, "%s-%s" %(tag, phone_tag), None)
        if value:
          element = etree.SubElement(node, phone_tag)
          element.text = value
    for tag in ['billing', 'shipping']:
      address = None
      for address_tag in address_tag_list:
        value = getattr(self, "%s-%s" %(tag, address_tag), None)
        if value:
          if address is None:
            address = etree.SubElement(node, 'address')
          if address_tag == "country":
            value = self.getIntegrationSite().getCategoryFromMapping(category = 'Country/%s' % value,
                                                                           create_mapping=True,
                                                                           create_mapping_line=True,
                                                                           ).split('/', 1)[-1]
          element = etree.SubElement(address, address_tag)
          element.text = value

class PersonNode(OxatisNode):

  def _setRelation(self, node):
    """
    Add the relation tag which link a person to an organisation
    """
    if getattr(self, "relation", None):
      element = etree.SubElement(node, 'relation')
      element.text = getattr(self, "relation")

  def _asXML(self):
    if getattr(self, 'country', None) is not None and not len(self.country):
      # Mapping is not done
      return ""

    xml = ""
    node = etree.Element('node', type="Person")

    # list of possible tags for a node
    tag_list = (
      'firstname', 'lastname',
    )
    self._setTagList(self, node, tag_list)

    self._generateCoordinatesXML(node)

    # category
    is_customer = getattr(self, "is_customer")
    if is_customer == "false":
      element = etree.SubElement(node, 'category')
      element.text = 'role/internal'
    else:
      element = etree.SubElement(node, 'category')
      element.text = 'role/client'

    # relation with organisation
    self._setRelation(node)

    xml += etree.tostring(node, pretty_print=True, encoding='utf-8')
    #LOG('Node asXML returns : %s' %(xml,), 300, "")
    return xml


class Organisation(OxatisNode):

  def _asXML(self):
    if getattr(self, 'country', None) is not None and not len(self.country):
      # Mapping is not done
      return ""

    xml = ""
    node = etree.Element('node', type="Organisation")

    self._setTagList(self, node, ['title',])
    self._generateCoordinatesXML(node)

    xml += etree.tostring(node, pretty_print=True, encoding='utf-8')
    #LOG('Node asXML returns : %s' %(xml,), 300, "")
    return xml


class Transaction(TransactionBrain):
  """
    This class allows to build the TioSafe XML of a Sale Order and to sync.
  """
  __allow_access_to_unprotected_subobjects__ = 1

  def __init__(self, object_type, context, **kw):
    TransactionBrain.__init__(self, object_type, context, **kw)
    self.reference = self.id

  def _setArrowTag(self, document=None, xml=None, source_tag='source',
      destination_tag='destination', category=''):
    """ This method build the XML of the arrow.
        Redefine here as for oxatis as a gid type is givent
    """
    # only work on the data of the document and not on its parent's data
    document = aq_base(document)
    sync_list = self.getTioSafeSynchronizationObjectList(object_type=["Person", "Organisation"])

    # create the arrow tag and set if exist source and destination
    arrow = etree.SubElement(xml, 'arrow', type=category)
    arrow_list = [(source_tag, 'source'), (destination_tag, 'destination')]
    for prop, tag in arrow_list:
      if getattr(document, prop, None) is not None:
        movement = etree.SubElement(arrow, tag)
        object_gid = getattr(document, prop)
        if object_gid != 'default_node':
          movement.text = object_gid
        else:
          movement.text = self.getDefaultOrganisationGID()


  def _asXML(self):
    transaction = etree.Element('transaction', type="Sale Order")
    tiosafe_sync_list = self.getTioSafeSynchronizationObjectList(object_type='Product')
    erp5_sync_list = self.getERP5SynchronizationObjectList(object_type='Product')
    integration_site = self.getIntegrationSite()

    # marker for checking property existency
    MARKER = object()

    # specific value
    self.stop_date = self.start_date
    self.reference = self.id
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

    module_id = "%s_module" %(portal_type)
    module = getattr(integration_site, module_id)


    getter_line_method = getattr(
        module,
        'get%sLineList' % (method_id,),
        MARKER,
    )
    if getter_line_method is not MARKER:
      # browse each transaction lines, build the sort element and set data
      parameter_kw = {'%s_id' % portal_type: str(self.getId()), }
      for line in getter_line_method(**parameter_kw):
        key_list = ['title', 'resource', 'reference', 'quantity', 'gross_price', 'vat', 'vat_price', 'net_price']
        value_list = [getattr(line, x, '') for x in key_list]
        movement_dict = {'context': line,}
        # set to None the '' value of the list
        for k, v in zip(key_list, value_list):
          movement_dict[k] = v or None
        if movement_dict.get('reference', None) is None:
          continue
        LOG("getter_line_method %s, id %s, movement_dict" %(getter_line_method,
                                                            self.getId(),), 300, movement_dict)
        # Compute the gid of the resource
        site = self.getIntegrationSite()
        resource_gid = site.product_module.getDestinationSectionValue().getGidFromObject(line, encoded=False)
        # Check the GID existence in the database
        signature = None
        for sync in tiosafe_sync_list:
          signature = sync.getSignatureFromGid(b16encode(resource_gid))
          if signature is not None:
            break
        if signature is None:
          resource_gid = self.getDefaultUnknownResourceGID()

        # after the work on the line set the resource value which will be
        # render in the xml
        movement_dict['resource'] = resource_gid

        # Work on vat
        if movement_dict['vat']:
          movement_dict['VAT'] = self.getVATCategory(movement_dict['vat'])

        if movement_dict['quantity'] is None:
          continue

        # Oxatis returns price with vat include, so compute the one without the va
        movement_dict['price'] = float(movement_dict['gross_price']) / (1 + float(movement_dict['vat']) / 100.0)

        # We might have a discount
        if movement_dict['gross_price'] != movement_dict['net_price']:
          # build another line for discount
          discount_gid = b16decode(erp5_sync_list[0].getGidFromObject(integration_site.getSourceCarrierValue()))
          discount_vat_incl_price = float(movement_dict['gross_price']) - float(movement_dict['net_price'])
          discount_price = discount_vat_incl_price / (1 + float(movement_dict['vat']) / 100.0)
          discount_dict = {'price': discount_price,
                           'quantity' : float(movement_dict['quantity']) * -1,
                           'resource' : discount_gid,
                           'title' : 'discount on %s / %s' %(movement_dict['title'], movement_dict['reference']),
                           'reference' : 'discount on %s / %s' %(movement_dict['title'], movement_dict['reference']),
                           'VAT' : movement_dict['VAT'],
                           }
          movement_list.append(discount_dict)


        # build the element which allows to sort
        movement_list.append(movement_dict)

    # Add delivery
    if int(float(getattr(self, "delivery_price", 0))) != 0:
      for erp5_sync in erp5_sync_list:
        try:
          delivery_gid = b16decode(erp5_sync.getGidFromObject(integration_site.getDestinationCarrierValue()))
          break
        except (ValueError, AttributeError):
          resource = None
      delivery_dict =  {'price': self.delivery_price,
                        'quantity' : 1,
                        'title' : self.delivery_title,
                        'reference' : self.delivery_title,
                        'resource' : delivery_gid,
                        'VAT' : self.getVATCategory(self.delivery_tax_rate)
                        }

      movement_list.append(delivery_dict)

    def cmp_resource(a,b):
      return cmp(a['resource'], b['resource'])

    movement_list.sort(cmp=cmp_resource)

    # the second part build the XML of the transaction
    # browse the ordered movement list and build the movement list as a result
    # the xml through of the line data in the dict
    for movement_dict in movement_list:
      movement = etree.SubElement(transaction, 'movement')
      # set arrow list on the movement
      if movement_dict.get("context", None) is not None:
        self._setArrowTagList(movement_dict['context'], movement)
      # if exist the following tags in the line dict, add them in the xml
      tag_list = ('resource', 'title', 'reference', 'quantity', 'price', 'VAT')
      for tag in tag_list:
        if tag in movement_dict:
          if movement_dict[tag] is not None:
            element = etree.SubElement(movement, tag)
            if tag == "price":
              element.text = "%.6f" % (float(movement_dict.get(tag, 0.0)),)
            elif tag == "quantity":
              element.text = "%.2f" % (float(movement_dict.get(tag, 0.0)),)
            else:
              element.text = movement_dict[tag]
      # add the categories to the movement
      for category_value in movement_dict.get('category', []):
        category = etree.SubElement(movement, 'category')
        category.text = category_value

    xml = etree.tostring(transaction, pretty_print=True, encoding='utf-8')
    #LOG("asXML returns transaction %s" %(xml,), 300, "")
    return xml
