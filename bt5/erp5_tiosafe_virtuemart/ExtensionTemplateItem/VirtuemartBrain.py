# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
#                Aurélien Calonne  <aurel@nexedi.com>
#                Mohamadou Mbengue <mohamadou@nexedi.com>
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
ResourceBrain = getBrain('TioSafeBrain', 'Resource', reload=1)
TransactionBrain = getBrain('TioSafeBrain', 'Transaction', reload=1)

class VirtuemartNode(NodeBrain):
  
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
        LOG("VirtuemartBrain.VirtuemartNode.__init__", ERROR, "Getting category for %s raise with msg = %s" %(self.country, msg))
        self.country = ""

  def _generateCoordinatesXML(self, node):
    """ Generates xml for phones, faxes and email """

    self._setTagList(self, node, ['email',])
    # Phones
    phone_tag_list = ['phone', 'cellphone']
    phone_list = []
    for tag in phone_tag_list:
      value = getattr(self, "%s" %(tag), None)
      if value:
        phone_list.append(value)
    phone_list.sort()
    for phone in phone_list:
      element = etree.SubElement(node, 'phone')
      element.text = phone

    # Fax
    value = getattr(self, "fax", None)
    if value:
      element = etree.SubElement(node, 'fax')
      element.text = value

    # Address
    address_tag_list = ['street', 'zip', 'city', 'country']
    address = None
    for address_tag in address_tag_list:
      value = getattr(self, "%s" %(address_tag), None)
      if value:
        if address_tag == "country": # find the mapping
          try:
            value = self.getIntegrationSite().getCategoryFromMapping(
              category = 'Country/%s' % value, create_mapping=True,
              create_mapping_line=True,
              )
            value = "/".join(value.split('/')[1:])
          except ValueError, msg:
            LOG("VirtuemartBrain.VirtuemartNode._generateCoordinatesXML", ERROR, "Getting category for %s raise with msg = %s" %(value, msg))
            #return ""

        if address is None:
          address = etree.SubElement(node, 'address')
        element = etree.SubElement(address, address_tag)
        element.text = value

class PersonNode(VirtuemartNode):

  def _setRelation(self, node):
    """
    Add the relation tag which link a person to an organisation
    """
    if getattr(self, "relation", None):
      element = etree.SubElement(node, 'relation')
      element.text = getattr(self, "relation")

  def _asXML(self):
    xml = ""
    node = etree.Element('node', type="Person")

    # list of possible tags for a node
    tag_list = (
      'firstname', 'lastname',
    )
    self._setTagList(self, node, tag_list)

    self._generateCoordinatesXML(node)
    
    """
    try:
      self._getAddressListAsXML(node)
    except  ValueError, msg:
      # Missing mapping
      LOG("VirtuemartBrain.PersonNode._asXML", ERROR, "Getting category for %s raise with msg = %s" %(ValueError, msg))
      #return None
    """

    # category
    element = etree.SubElement(node, 'category')
    element.text = 'role/client'

    # We must distinguish invoiced client from delivery client
    if getattr(self, "is_delivery", None) is not None:
      element = etree.SubElement(node, 'category')
      element.text = 'role/virtuemart_delivery'

    self._setRelation(node)
    
    xml += etree.tostring(node, pretty_print=True, encoding='utf-8')
    #LOG('Node asXML returns : %s' %(xml,), 300, "")
    return xml


class Organisation(VirtuemartNode):

  def _asXML(self):
    if getattr(self, 'country', None) is not None and not len(self.country):
      # Mapping is not done
      return ""

    xml = ""
    node = etree.Element('node', type="Organisation")

    self._setTagList(self, node, ['title',])
    self._generateCoordinatesXML(node)

    # We must distinguish invoiced client from delivery client
    if getattr(self, "is_delivery", None) is not None:
      element = etree.SubElement(node, 'category')
      element.text = 'role/virtuemart_delivery'

    xml += etree.tostring(node, pretty_print=True, encoding='utf-8')
    #LOG('Node asXML returns : %s' %(xml,), 300, "")
    return xml

class ProductResource(ResourceBrain):

  def _asXML(self):
    resource = etree.Element('resource', type="Product")

    # list of possible tags for an product
    tag_list = (
      'title', 'reference', 'ean13',
      'description',
    )
    self._setTagList(self, resource, tag_list)

    # marker for checking property existency
    MARKER = object()
    category_list = []
    """
    # build the list of categories
    
    if getattr(self, 'category', MARKER) is not MARKER:
      for category in self.category.split(SEPARATOR):
        category_list.append(category)
    """
    module_id = "%s_module" %(self.getPortalType().lower(),)
    module = getattr(self.context, module_id)

    get_category_method = "get%sCategoryList" % self.getPortalType()
    if getattr(module, get_category_method, MARKER) is not MARKER:
      # add category list
      parameter_kw = {"%s_id" %(self.getPortalType().replace(" ", "_").lower(),) : str(self.getId())}
      for element in getattr(module, get_category_method)(**parameter_kw):
        # XXX-Aurel : This code is bad as it assumes it will return a list in any case
        try:
          category = self.getIntegrationSite().getCategoryFromMapping(
            category=element.category, create_mapping=True
            )
        except ValueError:
          return None
        category_list.append(category)

    # order the category list
    category_list.sort()

    # add the categories to the product's xml
    for category_value in category_list:
      category = etree.SubElement(resource, 'category')
      category.text = category_value

    xml = etree.tostring(resource, pretty_print=True, encoding='utf-8')
    from zLOG import LOG
    LOG("Resource return xml %s" %(xml), 300, "")
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
        Redefine here as for ubercart as a gid type is given
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
    #self.reference = self.id
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

        # Retrieve the gid of the resource
        for tiosafe_sync in tiosafe_sync_list:
          try:
            brain_node = tiosafe_sync.getObjectFromId(line.product_id)
            resource_gid = brain_node.getGid()
            break
          except (ValueError, AttributeError):
            resource_gid = " Unknown"

        for erp5_sync in erp5_sync_list:
          try:
            resource = erp5_sync.getDocumentFromGid(b16encode(resource_gid))
            break
          except (ValueError, AttributeError):
            resource = None


        # after the work on the line set the resource value which will be
        # render in the xml
        movement_dict['resource'] = resource_gid

        # Work on vat
        if movement_dict['vat']:
          movement_dict['VAT'] = self.getVATCategory(movement_dict['vat'])

        if movement_dict['quantity'] is None:
          continue

        movement_dict['price'] = movement_dict['net_price']
       
        # build the element which allows to sort
        movement_list.append(movement_dict)
    
    # Add Discount
    if self.discount_price > 0:
      discount_gid = b16decode(erp5_sync.getGidFromObject(integration_site.getSourceCarrierValue()))
      discount_dict =  {'price': self.discount_price,
                        'quantity' : -1,
                        'title' : '%s' % (self.discount_title),
                        'reference' : '%s' % (self.discount_title),
                        'resource' : discount_gid,
                        'VAT' : self.getVATCategory(self.discount_tax_rate)
                        }

      movement_list.append(discount_dict)
    # Add delivery
    if self.delivery_price > 0:
      delivery_gid = b16decode(erp5_sync.getGidFromObject(integration_site.getDestinationCarrierValue()))
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
      #for category_value in movement_dict['category']:
      for category_value in movement_dict.get('category', []):
        LOG("category_value %s" %(category_value), 300, "")
        category = etree.SubElement(movement, 'category')
        category.text = category_value
      
    xml = etree.tostring(transaction, pretty_print=True, encoding='utf-8')
    LOG("asXML returns transaction %s" %(xml,), 300, "")
    return xml
