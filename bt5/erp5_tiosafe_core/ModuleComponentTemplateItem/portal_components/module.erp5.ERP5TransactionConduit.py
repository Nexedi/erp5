# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#               Hervé Poulain <herve@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################
from base64 import b16encode
from copy import deepcopy

from erp5.component.module.TioSafeBaseConduit import TioSafeBaseConduit
from erp5.component.module.SyncMLConstant import XUPDATE_INSERT_OR_ADD_LIST

class ERP5TransactionConduit(TioSafeBaseConduit):
  """
    This is the conduit use to synchonize tiosafe sale orders and ERP5
  """
  def __init__(self):
    # Define the object_tag element to add object
    self.xml_object_tag = 'transaction'

  def getObjectAsXML(self, object, domain): # pylint: disable=redefined-builtin
    return object.Transaction_asTioSafeXML(context_document=domain)

  def updateNode(self, xml=None, object=None, previous_xml=None, force=0, # pylint: disable=redefined-builtin
      simulate=0,  **kw):
    raise Exception('updateNode: Impossible to update transaction')


  def deleteNode(self, xml=None, object=None, previous_xml=None, force=0, # pylint: disable=redefined-builtin
      simulate=0,  **kw):
    raise Exception('deleteNode: Impossible to delete transaction')


  def _createContent(self, xml=None, object=None, object_id=None, sub_object=None, # pylint: disable=redefined-builtin
      reset_local_roles=0, reset_workflow=0, simulate=0, **kw):
    """
      This is the method calling to create an object
    """
    if object_id is None:
      object_id = self.getAttribute(xml, 'id')
    if True: # object_id is not None:
      if sub_object is None and object_id:
        try:
          sub_object = object._getOb(object_id)
        except (AttributeError, KeyError, TypeError):
          sub_object = None
      if sub_object is None: # If so, it doesn't exist
        portal_type = ''
        if xml.xpath('local-name()') == self.xml_object_tag:
          portal_type = self.getObjectType(xml)
        elif xml.xpath('name()') in XUPDATE_INSERT_OR_ADD_LIST: # Deprecated ???
          portal_type = self.getXupdateContentType(xml) # Deprecated ???
        sub_object, reset_local_roles, reset_workflow = self.constructContent(
            object,
            object_id,
            portal_type,
        )

        # Define the trade condition by using the one defined on IS
        integration_site = self.getIntegrationSite(kw.get('domain'))
        if portal_type == "Sale Order":
          sub_object.setSpecialise(integration_site.getSourceTrade())
          sub_object.SaleOrder_applySaleTradeCondition()
        # Mapping between tag and element
        node_dict = {
            'arrow': self.visitArrow,
            'movement': self.visitMovement,
        }
        # if exist namespace retrieve only the tag
        index = 0
        if xml.nsmap not in [None, {}]:
          index = -1

        # Browse the list of arrows and movements
        for node in xml.getchildren():
          # Only works on right tags, and no on the comments, ...
          if not isinstance(node.tag, str):
            continue
          # Build the slipt list of a tag to test
          # Build the tag (without is Namespace)
          tag = node.tag.split('}')[index]
          # Treat sub-element
          if len(node.getchildren()):
            if tag in node_dict:
              node_dict[tag](document=sub_object, xml=node, **kw)
            else:
              raise ValueError("This is an unknown sub-element %s on %s" %(tag, sub_object.getPath()))
          if tag == 'currency':
            link_object = object.portal_catalog.getResultValue(
                portal_type='Currency',
                reference=node.text.encode('utf-8'),
            )
            sub_object.setPriceCurrencyValue(link_object)
          elif tag in ['start_date', 'stop_date']:
            if not node.text:
              node.text = None
          elif tag  == "payment_mode":
            sub_object.setPaymentConditionPaymentMode(node.text)

      # Build the content of new Sale Order
      self.newObject(
          object=sub_object,
          xml=xml,
          simulate=simulate,
          reset_local_roles=reset_local_roles,
          reset_workflow=reset_workflow,
      )
    return sub_object


  def afterNewObject(self, object): # pylint: disable=redefined-builtin
    """ Confirm the sale order and, add the grants on this one. """
    if object.getPortalType() in ['Sale Order',]:
      object.confirm()
    object.updateLocalRolesOnSecurityGroups()


  def visitArrow(self, document=None, xml=None, **kw):
    """ Manage the addition of sources and destination in the Sale Orders. """
    # if exist namespace retrieve only the tag
    index = 0
    if xml.nsmap not in [None, {}]:
      index = -1

    # retrieve the integration site
    domain = kw.get('domain')
    integration_site = self.getIntegrationSite(domain
)
    # use the setters of source and destination in terms of the category
    sync_object_list = self.getSynchronizationObjectListForType(kw.get('domain'), 'Person', 'publication') + \
                       self.getSynchronizationObjectListForType(kw.get('domain'), 'Organisation', 'publication')
    category = xml.get('type')
    if category != "":
      if category == 'Ownership':
        arrow_dict = {
        'source': {
          'synchronization': sync_object_list,
          'setter': document.setSourceSectionValue,
          'free_text_setter': document.setSourceSectionFreeText},
        'destination': {
          'synchronization': sync_object_list,
          'setter': document.setDestinationSectionValue,
          'free_text_setter': document.setDestinationSectionFreeText},
          }
      elif category == 'Payment':
        arrow_dict = {
        'source': {
          'synchronization': sync_object_list,
          'setter': document.setSourcePaymentValue,
          'free_text_setter': document.setSourcePaymentFreeText},
        'destination': {
          'synchronization': sync_object_list,
          'setter': document.setDestinationPaymentValue,
          'free_text_setter': document.setDestinationPaymentFreeText},
        }
      elif category == 'Administration':
        arrow_dict = {
        'source': {
          'synchronization': sync_object_list,
          'setter': document.setSourceAdministrationValue,
          'free_text_setter': document.setSourceAdministrationFreeText},
        'destination': {
          'synchronization': sync_object_list,
          'setter': document.setDestinationAdministrationValue,
          'free_text_setter': document.setDestinationAdministrationFreeText},
        }
      elif category == 'Decision':
        arrow_dict = {
        'source': {
          'synchronization': sync_object_list,
          'setter': document.setSourceDecisionValue,
          'free_text_setter': document.setSourceDecisionFreeText},
        'destination': {
          'synchronization': sync_object_list,
          'setter': document.setDestinationDecisionValue,
          'free_text_setter': document.setDestinationDecisionFreeText},
        }
      else:
        raise Exception('visitArrow: Unexpected Category %s' %(category))
    else:
      arrow_dict = {
      'source': {
        'synchronization': sync_object_list,
        'setter': document.setSourceValue,
        'free_text_setter': document.setSourceFreeText},
      'destination': {
        'synchronization': sync_object_list,
        'setter': document.setDestinationValue,
        'free_text_setter': document.setDestinationFreeText},
      }

    # browse the xml and save the source and destination in the sale order
    integration_site = self.getIntegrationSite(kw.get('domain'))
    default_source = integration_site.getSourceAdministrationValue()
    default_org_gid = integration_site.organisation_module.getSourceSectionValue().getGidFromObject(default_source, encoded=False)
    default_node = integration_site.getDestinationValue()

    for subnode in xml.getchildren():
      # only works on tags, no on the comments or other kind of tag
      if not isinstance(subnode.tag, str):
        continue
      tag = subnode.tag.split('}')[index]

      if tag in arrow_dict:
        # retrieve the corresponding
        synchronization_list = arrow_dict[tag]['synchronization']
        link_object = None
        link_gid = subnode.text.encode('utf-8')
        if link_gid == default_org_gid:
          link_object = default_source
        else:
          for synchronization in synchronization_list:
            # encode to the output type
            if getattr(synchronization, 'getDocumentFromGid', None) is not None:
              link_object = synchronization.getDocumentFromGid(b16encode(link_gid))
              #LOG("trying to get %s from %s, got %s" %(link_gid, synchronization.getPath(), link_object), 300, "This is for category type %s" %(category))
              if link_object is not None:
                break

        if link_object is None:
          arrow_dict[tag]['free_text_setter'](link_gid)
          link_object = default_node

        # set person to the sale order
        arrow_dict[tag]['setter'](link_object)


  def visitMovement(self, document=None, xml=None, **kw):
    """ Manage the addition of the Sale Order Line. """

    # dictionary of the value of a movement
    movement_dict_value = {'category': []}

    # if exist namespace retrieve only the tag
    index = 0
    if xml.nsmap not in [None, {}]:
      index = -1

    integration_site = self.getIntegrationSite(kw.get('domain'))
    default_resource = integration_site.getResourceValue()
    default_resource_gid = integration_site.product_module.getSourceSectionValue().getGidFromObject(default_resource, encoded=False)

    # browse the xml and save the sale order line values
    for subnode in xml.getchildren():
      # only works on tags, no on the comments or other kind of tag
      if not isinstance(subnode.tag, str):
        continue
      tag = subnode.tag.split('}')[index]
      if tag == 'resource':
        # encode to the output type
        link_gid = subnode.text #.encode('utf-8')
        if link_gid == ' Service Discount':
          link_object = integration_site.getSourceCarrierValue()
        elif link_gid == ' Service Delivery':
          link_object = integration_site.getDestinationCarrierValue()
        elif link_gid == default_resource_gid:
          link_object = default_resource
        else:
          synchronization_list = self.getSynchronizationObjectListForType(kw.get('domain'), 'Product', 'publication')
          for synchronization in synchronization_list:
            link_object = synchronization.getDocumentFromGid(b16encode(link_gid))
            if link_object is not None:
              break
        # in the worse case save the line with the unknown product
        if link_object is None:
          raise ValueError("Impossible to find related resource for gid %s" % link_gid)

        # set the resource in the dict
        movement_dict_value[tag] = link_object
      elif tag == "VAT":
        vat_category = document.portal_categories.base_amount.trade.base.taxable['vat']
        vat = vat_category[subnode.text]
        movement_dict_value['vat'] = vat
      elif tag == 'category':
        # set categories in the list
        if subnode.text is not None:
          movement_dict_value[tag].append(subnode.text)
      else:
        # set line values in the dict
        if subnode.text is not None:
          movement_dict_value[tag] = subnode.text#.encode('utf-8')
          #LOG("visitMovement", 300, "movement_dict_value = %s" %(movement_dict_value))
    if 'quantity' not in movement_dict_value:
      return

    # no variations will be use for the unknown product
    if movement_dict_value['resource'] == default_resource:
      movement_dict_value['category'] = []

    # Create the new Sale Order Line
    sale_order_line = document.newContent(portal_type='Sale Order Line')

    # define the setters of the sale order line
    mapping_of_setter = {
        'title': sale_order_line.setTitle,
        'reference': sale_order_line.setReference,
        'resource': sale_order_line.setResourceValue,
        'description': sale_order_line.setDescription,
        'vat': sale_order_line.setBaseContributionValue,
        'quantity': sale_order_line.setQuantity,
        'price': sale_order_line.setPrice,
    }

    # second, specific work on sale order line or on cell
    if len(movement_dict_value['category']):
      # set the resource on the sale order line
      mapping_of_setter['resource'](movement_dict_value['resource'])
      # work on variations
      variation_category_list = list(set(
          deepcopy(movement_dict_value['category'])
      ))
      #variation_category_list.sort() # XXX: The set remove the order
      sale_order_line.setVariationCategoryList(variation_category_list)
      variation_category_list = sale_order_line.getVariationCategoryList()
      # create the cell or raise if it's not possible
      cell = sale_order_line.newCell(
        base_id='movement',
        portal_type='Sale Order Cell',
        *variation_category_list
        )

      # set values on the cell
      cell.setCategoryList(variation_category_list)
      cell.setMembershipCriterionCategoryList(variation_category_list)
      cell.setMembershipCriterionBaseCategoryList(
          sale_order_line.getVariationBaseCategoryList(),
      )
      cell.setMappedValuePropertyList(['price', 'quantity'])
      mapping_of_setter['quantity'] = cell.setQuantity
      mapping_of_setter['price'] = cell.setPrice

    # set on the sale order line or on cell the values
    for key in movement_dict_value:
      if key in mapping_of_setter:
        mapping_of_setter[key](movement_dict_value[key])


  def editDocument(self, object=None, **kw): # pylint: disable=redefined-builtin
    """
      This is the default editDocument method. This method
      can easily be overwritten.
    """
    # Mapping of the PropertySheet
    mapping = {
        'title': 'title',
        'start_date': 'start_date',
        'stop_date': 'stop_date',
        'reference': 'reference',
        'causality': 'comment',
    }
    property_ = {}
    # Translate kw with the good PropertySheet
    for k, v in kw.items():
      k = mapping.get(k, k)
      property_[k] = v
    object._edit(**property_)