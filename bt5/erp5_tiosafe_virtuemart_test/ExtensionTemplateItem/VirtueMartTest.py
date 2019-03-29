##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
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

from lxml import etree
from cStringIO import StringIO
from zLOG import LOG, INFO, ERROR
from Acquisition import aq_base
import transaction 
from DateTime import DateTime

VIRTUEMART_XSD_PATH="portal_skins/erp5_tiosafe_virtuemart_test/XSD/"

ORGANISATION_PROPERTY_DEFINITION = (
        'id',
        'title',
        'reference',
        'email',
        'street',
        'zip',
        'city',
        'country',
        'phone',
)

PERSON_PROPERTY_DEFINITION = (
        'id',
        'firstname',
        'lastname',
        'email',
        'street',
        'zip',
        'city',
        'country',
        'company_id',
        'company',
        'category',
)

PRODUCT_PROPERTY_DEFINITION = (
        'id',
        'reference',
        'title',
        'sale_price',
        'purchase_price',
        'description',
        'category',
)



ORDER_PROPERTY_DEFINITION = (
        'id',
        'reference',
        'start_date',
        'currency',
        'billing_firstname',
        'billing_lastname',
        'billing_company',
        'billing_country',
        'billing_user_email',
        'payment_method',
        'primary_email',
        'delivery_title',
        'delivery_price',
        'delivery_tax_rate',
        'discount_code',
        'discount_title',
        'discount_price',
        'discount_tax_rate',
        'shipping_company',
        'shipping_country',
        'shipping_firstname',
        'shipping_lastname',
        'user_email',
)

ORDER_LINE_PROPERTY_DEFINITION = (
        'id',
        'reference',
        'id_product',
        'title',
        'quantity',
        'currency',
        'gross_price',
        'net_price',
        'vat',
        'vat_price',
)

class VirtueMartTestConnector:

  def __init__(self):
    """
    """
    from Products.ERP5.ERP5Site import getSite
    self.context = getSite()
  
  def getPropertySheetDefinitionList(self, type):
    definition_dict = {"organisation" : ORGANISATION_PROPERTY_DEFINITION,
                       "person" : PERSON_PROPERTY_DEFINITION,
                       "product" : PRODUCT_PROPERTY_DEFINITION,
                       "order" : ORDER_PROPERTY_DEFINITION,
                       "order_line" : ORDER_LINE_PROPERTY_DEFINITION}
    return definition_dict[type]

  def validateXMLScheme(self, xml, xsd_filename):
    """
    Validate generated xml agains XSD provided by virtuemart
    """
    xsd = self.context.restrictedTraverse(VIRTUEMART_XSD_PATH+xsd_filename)
    xml_schema = ''.join(xsd.data)
    xml_schema = StringIO(xml_schema)
    xml_schema = etree.parse(xml_schema)
    xml_schema = etree.XMLSchema(xml_schema)
    xml_element = etree.XML(xml)
    validated = xml_schema.validate(xml_element)
    if validated is False:
      LOG("validateXMLSchema failed with", ERROR, "%s, xsd = %s\nxml = %s\n" %(xml_schema.error_log.filter_from_errors()[0], xsd.data, xml))
    assert validated is True
    return validated

  def generateResultHeader(self):
    # generate xml
    root = etree.Element("xml")
    # Header part
    return root

  def getPersonList(self, *args, **kw):
    if kw.has_key('person_id'):
      person_id = kw["person_id"]
      # retrieve the person inside the test module
      person_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(id=person_id,
                                                                                       validation_state="validated",
                                                                                       portal_type="Virtuemart Test Person")
    else:
      person_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(portal_type="Virtuemart Test Person",
                                                                                       validation_state="validated")
    root = self.generateResultHeader()
    for person in person_list:
      person = person.getObject()
      if not person.getTitle().startswith("Delivered"):
        person_element = etree.SubElement(root, "object")      
        for prop in self.getPropertySheetDefinitionList("person"):
          prop_xml = etree.SubElement(person_element, prop)
          value = getattr(aq_base(person), prop, "")
          #LOG("Viewing value ", INFO, "%s" % value)
          if isinstance(value, str):
            prop_xml.text = value.decode('utf-8')
          else:
            prop_xml.text = str(value)

    xml = etree.tostring(root, pretty_print=True)
    #persons_xml = etree.tostring(root, pretty_print=True)
    #self.validateXMLScheme(persons_xml, "PersonList.xsd")
    return "", xml

  def updatePerson(self, *args, **kw):
    LOG("Viewing updatePerson ", INFO, "kw: %s" %(kw))
    if not kw.has_key('person_id'):
      raise ValueError("No parameter person_id given, got %s / %s" %(args, kw))
    person_id = kw["person_id"]
    # get corresponding person from test module
    person_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(id=person_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Virtuemart Test Person")
    if len(person_list) != 1:
      raise KeyError(person_id)
    else:
      person = person_list[0].getObject()
    root = self.generateResultHeader()
    person_dict = {}
    for key in kw.keys():
      if key not in ["start_date", "stop_date", "person_id", "relation"]:
        person_dict[key] = kw[key]

    if kw.has_key('relation'):
      if kw["relation"] == 'NULL' or kw["relation"]=='':
        person_dict["company"]=" "
      else:
        person_dict["company"]=kw["relation"]
      
    LOG("Editing person %s with %s" %(person.getPath(), person_dict,), 300, "\n")
    person.edit(**person_dict)
    transaction.commit()
    # Return default xml
    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    return "", xml

  def deletePerson(self, *args, **kw):
    if not kw.has_key('person_id'):
      raise ValueError("No parameter person_id given, got %s / %s" %(args, kw))
    person_id = kw['person_id']
    # get corresponding person from test module
    person_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(id=person_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Virtuemart Test Person")
    if len(person_list) != 1:
      raise KeyError(resource_id)
    else:
      person = person_list[0].getObject()
      person.invalidate()
    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    return "", xml
  '''
  def getPersonAddressListOld(self, *args, **kw):
    if not kw.has_key('person_id'):
      raise ValueError, "No person_id given, got %s / %s" %(args, kw)
    person_id = kw["person_id"]
    # retrieve the person inside the test module
    person_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(id=person_id,
                                                                                     validation_state="validated",
                                                                                     portal_type="Virtuemart Test Person")
    root = self.generateResultHeader()
    for person in person_list:
      person = person.getObject()
      if not person.getTitle().startswith("Delivered"):
        person_element = etree.SubElement(root, "object")      
        for prop in self.getPropertySheetDefinitionList("person"):
          if prop in ['street', 'zip', 'city', 'country']:
            prop_xml = etree.SubElement(person_element, "id")
            prop_xml.text = str(person.getId())
            prop_xml = etree.SubElement(person_element, prop)
            value = getattr(aq_base(person), prop, "")
            if isinstance(value, str):
              prop_xml.text = value.decode('utf-8')
            else:
              prop_xml.text = str(value)

    xml = etree.tostring(root, pretty_print=True)
    #persons_xml = etree.tostring(root, pretty_print=True)
    #self.validateXMLScheme(persons_xml, "PersonList.xsd")
    return "", xml
  '''
  def getPersonAddressList(self, *args, **kw):
    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    return "", xml

  def createAddress(self, *args, **kw):
    if not kw.has_key('person_id'):
      raise ValueError("No person_id given, got %s / %s" %(args, kw))
    keywords = {} 
    if kw.has_key('street'):
      keywords["street"] = kw['street'].strip('"').strip("'")
    if kw.has_key('zip'):
      keywords["zip"] = kw['zip'].strip('"').strip("'")
    if kw.has_key('city'):
      keywords["city"] = kw['city'].strip('"').strip("'")
    if kw.has_key('country'):
      keywords["country"] = kw['country'].strip('"').strip("'")
    '''
    resource = self.context.getPortalObject().virtuemart_test_module.newContent(portal_type="Virtuemart Test Product")
    resource.edit(**keywords)
    resource.validate()
    '''
    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    return "", xml

  def updateAddress(self, *args, **kw):
    LOG("Viewing updateAddress ", INFO, "kw: %s" %(kw))
    if not kw.has_key('person_id') :
      raise ValueError("No parameter person_id given, got %s / %s" %(args, kw))
    keywords = {} 
    if kw.has_key('street'):
      keywords["street"] = kw['street'].strip('"').strip("'")
    if kw.has_key('zip'):
      keywords["zip"] = kw['zip'].strip('"').strip("'")
    if kw.has_key('city'):
      keywords["city"] = kw['city'].strip('"').strip("'")
    if kw.has_key('country'):
      keywords["country"] = kw['country'].strip('"').strip("'")

    person_id = kw['person_id']
    # retrieve the address inside the test module
    person_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(id=person_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Virtuemart Test Person")
    if len(person_list) != 1:
      raise KeyError(person_id)
    else:
      person = person_list[0].getObject()
    person.edit(**keywords)
    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    return "", xml

  def getDeliveredPersonList(self, *args, **kw):
    #LOG("Viewing person ", INFO, "kw: %s" %(kw))
    if kw.has_key('person_id'):
      person_id = kw["person_id"]
      # retrieve the person inside the test module
      person_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(id=person_id,
                                                                                       validation_state="validated",
                                                                                       portal_type="Virtuemart Test Person")
    else:
      person_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(portal_type="Virtuemart Test Person",
                                                                                       validation_state="validated")
    root = self.generateResultHeader()
    for person in person_list:
      person = person.getObject()
      if person.getTitle().startswith("Delivered"):
        person_element = etree.SubElement(root, "object")      
        for prop in self.getPropertySheetDefinitionList("person"):
          prop_xml = etree.SubElement(person_element, prop)
          value = getattr(aq_base(person), prop, "")
          if isinstance(value, str):
            prop_xml.text = value.decode('utf-8')
          else:
            prop_xml.text = str(value)

    xml = etree.tostring(root, pretty_print=True)
    #persons_xml = etree.tostring(root, pretty_print=True)
    #self.validateXMLScheme(persons_xml, "PersonList.xsd")
    return "", xml

  def getOrganisationList(self, *args, **kw):
    #LOG("Viewing organisation %s" %(kw["organisation_id"]), INFO)
    if kw.has_key('organisation_id'):
      organisation_id = kw["organisation_id"]
      # retrieve the person inside the test module
      organisation_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(id=organisation_id,
                                                                                       validation_state="validated",
                                                                                       portal_type="Virtuemart Test Organisation")
    else:
      organisation_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(portal_type="Virtuemart Test Organisation",
                                                                                       validation_state="validated")
    
    root = self.generateResultHeader()
    for organisation in organisation_list:
      organisation = organisation.getObject()
      if not organisation.getTitle().startswith("Delivered"):
        organisation_element = etree.SubElement(root, "object")      
        for prop in self.getPropertySheetDefinitionList("organisation"):
          prop_xml = etree.SubElement(organisation_element, prop)
          value = getattr(aq_base(organisation), prop, "")
          if isinstance(value, str):
            prop_xml.text = value.decode('utf-8')
          else:
            prop_xml.text = str(value)

    xml = etree.tostring(root, pretty_print=True)
    #organisations_xml = etree.tostring(root, pretty_print=True)
    #self.validateXMLScheme(persons_xml, "OrganisationList.xsd")
    return "", xml

  def getDeliveredOrganisationList(self, *args, **kw):
    if kw.has_key('organisation_id'):
      organisation_id = kw["organisation_id"]
      # retrieve the person inside the test module
      organisation_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(id=organisation_id,
                                                                                       validation_state="validated",
                                                                                       portal_type="Virtuemart Test Organisation")
    else:
      organisation_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(portal_type="Virtuemart Test Organisation",
                                                                                       validation_state="validated")
    root = self.generateResultHeader()
    for organisation in organisation_list:
      organisation = organisation.getObject()
      if organisation.getTitle().startswith("Delivered"):
        organisation_element = etree.SubElement(root, "object")      
        for prop in self.getPropertySheetDefinitionList("organisation"):
          prop_xml = etree.SubElement(organisation_element, prop)
          value = getattr(aq_base(organisation), prop, "")
          if isinstance(value, str):
            prop_xml.text = value.decode('utf-8')
          else:
            prop_xml.text = str(value)

    xml = etree.tostring(root, pretty_print=True)
    #organisations_xml = etree.tostring(root, pretty_print=True)
    #self.validateXMLScheme(persons_xml, "OrganisationList.xsd")
    return "", xml

  #
  # This is the Product part
  #
  def getProductList(self, *args, **kw):
    if kw.has_key('product_id'):
      product_id = kw["product_id"]
      # retrieve the person inside the test module
      resource_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(id=product_id,
                                                                                         portal_type="Virtuemart Test Product",
                                                                                         validation_state="validated")
    else:
      resource_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(portal_type="Virtuemart Test Product",
                                                                                   validation_state="validated")

    root = self.generateResultHeader()
    for resource in resource_list:
      resource = resource.getObject()
      product = etree.SubElement(root, "object")      
      for prop in self.getPropertySheetDefinitionList("product"):
        prop_xml = etree.SubElement(product, prop)
        value = getattr(aq_base(resource), prop, "")
        if isinstance(value, str):
          prop_xml.text = value.decode('utf-8')
        else:
          prop_xml.text = str(value)

    xml = etree.tostring(root, pretty_print=True)
    #products_xml = etree.tostring(products, pretty_print=True)
    #self.validateXMLScheme(products_xml, "ProductList.xsd")
    return "", xml

  def createProduct(self, *args, **kw):
    if not kw.has_key('reference'):
      raise ValueError("No reference passed to createProduct, got %s / %s" %(args, kw))
    keywords = {} 
    keywords["reference"] = kw['reference'].strip('"').strip("'")
    if kw.has_key('title'):
      keywords["title"] = kw['title'].strip('"').strip("'")
    if kw.has_key('description'):
      keywords["description"] = kw['description'].strip('"').strip("'")
    if kw.has_key('sale_price'):
      keywords["sale_price"] = kw['sale_price']
    if kw.has_key('  purchase_price'):
      keywords["purchase_price"] = kw['purchase_price']
    #XXX Test if a product with the same reference does not exist in the plugin first
    resource = self.context.getPortalObject().virtuemart_test_module.newContent(portal_type="Virtuemart Test Product")
    resource.edit(**keywords)
    resource.validate()
    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    return "", xml


  def deleteProduct(self, *args, **kw):
    if not kw.has_key('product_id'):
      raise ValueError("No parameter product_id given, got %s / %s" %(args, kw))
    resource_id = kw['product_id']
    # retrieve the product inside the test module
    resource_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(id=resource_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Virtuemart Test Product")
    if len(resource_list) != 1:
      raise KeyError(resource_id)
    else:
      resource = resource_list[0].getObject()
      resource.invalidate()
    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    return "", xml

  def updateProduct(self, *args, **kw):
    if not kw.has_key('product_id') :
      raise ValueError("No parameter product_id given, got %s / %s" %(args, kw))
    keywords = {} 
    if kw.has_key('title'):
      keywords["title"] = kw['title'].strip('"').strip("'")
    if kw.has_key('description'):
      keywords["description"] = kw['description'].strip('"').strip("'")

    resource_id = kw['product_id']
    # retrieve the product inside the test module
    resource_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(id=resource_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Virtuemart Test Product")
    if len(resource_list) != 1:
      raise KeyError(resource_id)
    else:
      resource = resource_list[0].getObject()
    resource.edit(**keywords)
    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    return "", xml

  def checkCategoryExistency(self, *args, **kw):
    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    return "", xml

  def createProductCategory(self, *args, **kw):
    if not kw.has_key('product_id'):
      raise ValueError("No parameter product_id given, got %s / %s" %(args, kw))
    if not kw.has_key('base_category') or not kw.has_key('variation'):
      raise ValueError("No parameter base_category or variation given, got %s " %(kw))
    base_category = kw['base_category'].strip('"').strip("'")
    variation = kw['variation'].strip('"').strip("'")
    category = "%s/%s" % (base_category, variation)
    resource_id = kw['product_id']
    resource_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(id=resource_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Virtuemart Test Product")
    if len(resource_list) != 1:
      raise KeyError(resource_id)
    else:
      resource = resource_list[0].getObject()
    #XXX Test if the variation does not exist in the plugin first
    variation = resource.newContent(portal_type="Virtuemart Test Product Variation")
    variation.edit(category=category)
    variation.validate()
    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    return "", xml

  def deleteProductCategory(self, *args, **kw):
    if not kw.has_key('product_id'):
      raise ValueError("No parameter product_id given, got %s / %s" %(args, kw))
    if not kw.has_key('base_category') or not kw.has_key('variation'):
      raise ValueError("No parameter base_category or variation given, got %s" %(kw))
    base_category = kw['base_category'].strip('"').strip("'")
    variation = kw['variation'].strip('"').strip("'")
    category = "%s/%s" % (base_category, variation)
    resource_id = kw['product_id']
    resource_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(id=resource_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Virtuemart Test Product")
    if len(resource_list) != 1:
      raise KeyError(resource_id)
    else:
      resource = resource_list[0].getObject()

    
    variation_list = resource.searchFolder(validation_state="validated",
                                           portal_type="Virtuemart Test Product Variation")
    for variation in variation_list:
      if variation.getObject().getCategory()==category:
        resource.manage_delObjects(ids=[variation.getId(),])
        #variation.invalidate()
        break
    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    return "", xml

  def getProductCategoryList(self, *args, **kw):
    if not kw.has_key('product_id') and not kw.has_key('group_id'):
      raise ValueError("No parameter product_id given, got %s / %s" %(args, kw))
    if kw.has_key('product_id'):
      resource_id = kw['product_id']
    else:
      resource_id = kw['group_id']
    # retrieve the product inside the test module
    resource_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(id=resource_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Virtuemart Test Product")
    if len(resource_list) != 1:
      raise KeyError(resource_id)
    else:
      resource = resource_list[0].getObject()

    variation_list = resource.searchFolder(validation_state="validated",
                                           portal_type='Virtuemart Test Product Variation')
    
    root = self.generateResultHeader()
    for attribute in variation_list:
      attribute = attribute.getObject()
      variation = etree.SubElement(root, "object")  
      #prop_xml = etree.SubElement(variation, "id")
      #prop_xml.text = str(attribute.getId())
      prop_xml = etree.SubElement(variation, "category")
      value = attribute.getCategory()
      if isinstance(value, str):
        prop_xml.text = value.decode('utf-8')
      else:
        prop_xml.text = str(value)
    xml = etree.tostring(root, pretty_print=True)
    return "", xml

  def getLastID(self, *args, **kw):
    if not kw.has_key('type'):
      raise ValueError("No parameter type given, got %s / %s" %(args, kw))
    type = kw['type']

    last_id = -1
    if type == 'Product':
      resource_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(portal_type="Virtuemart Test Product")
      resource_id_list = []
      for resource in resource_list:
        resource_id_list.append(resource.getObject().getId())
      resource_id_list.sort()
      if len(resource_list) > 0:
        last_id = resource_id_list[-1]        
    elif type == 'Person':
      person_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(portal_type="Virtuemart Test Person")
      person_id_list = []
      for person in person_list:
        person_id_list.append(person.getObject().getId())
      person_id_list.sort()
      if len(person_list) > 0:
        last_id = person_id_list[-1]

    root = self.generateResultHeader()
    elt_last_id = etree.SubElement(root, "object")
    prop_xml = etree.SubElement(elt_last_id, "id")
    prop_xml.text = str(last_id)
    xml = etree.tostring(root, pretty_print=True)
    return "", xml

  def getLastProductID(self, *args, **kw):
    resource_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(portal_type="Virtuemart Test Product")
    resource_id_list = []
    for resource in resource_list:
      resource_id_list.append(resource.getObject().getId())
    resource_id_list.sort()
    if len(resource_list) > 0:
      last_id = resource_id_list[-1]
    else:
      last_id = -1

    root = self.generateResultHeader()
    product_last_id = etree.SubElement(root, "object")
    prop_xml = etree.SubElement(product_last_id, "id")
    prop_xml.text = str(last_id)
    xml = etree.tostring(root, pretty_print=True)
    return "", xml

  #
  # This is the Order part
  #
  def getSaleOrderList(self, *args, **kw):
    sale_order_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(validation_state='validated',
                                                                                         portal_type="Virtuemart Test Sale Order")
    root = self.generateResultHeader()

    # must put date into order_list
    for sale_order in sale_order_list:
      sale_order = sale_order.getObject()
      #order_date = DateTime(sale_order.getStartDate())
      order = etree.SubElement(root, "object")      
      for prop in self.getPropertySheetDefinitionList("order"):
        prop_xml = etree.SubElement(order, prop)
        value = getattr(aq_base(sale_order), prop, "")
        if isinstance(value, str):
          prop_xml.text = value.decode('utf-8')
        else:
          prop_xml.text = str(value)


    xml = etree.tostring(root, pretty_print=True)
    #orders_xml = etree.tostring(orders, pretty_print=True)
    #self.validateXMLScheme(orders_xml, "SaleOrderList.xsd")
    #LOG("returning xml", 300, "\n%s" %(xml))
    return "", xml


  def _getOrderLineDetails(self, sale_order, xml):
    for line in sale_order.contentValues():
      item = etree.SubElement(xml, "<object>")
      for prop in self.getPropertySheetDefinitionList("order_line"):
        prop_xml = etree.SubElement(item, prop)
        value = getattr(aq_base(line), prop, "")
        prop_xml.text = value.decode('utf-8')


  def getSaleOrderLineList(self, *args, **kw):
    if not kw.has_key('sale_order_id'):
      raise ValueError("No parameter sale_order_id given, got %s / %s" %(args, kw))
    sale_order_id = kw['sale_order_id']

    sale_order_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(id=sale_order_id,
                                                                 validation_state='validated',
                                                                 portal_type="Virtuemart Test Sale Order")
    if len(sale_order_list) != 1:
      raise KeyError(sale_order_id)
    else:
      sale_order_object = sale_order_list[0].getObject()

    # retrieve the order inside the test module
    sale_order_line_list = sale_order_object.searchFolder(portal_type="Virtuemart Test Sale Order Item")

    root = self.generateResultHeader()
    # Data part
    # must put date into order_list
    for sale_order_line in sale_order_line_list:
      sale_order_line = sale_order_line.getObject()
      order_line = etree.SubElement(root, "object")      
      for prop in self.getPropertySheetDefinitionList("order_line"):
        prop_xml = etree.SubElement(order_line, prop)
        value = getattr(aq_base(sale_order_line), prop, "")
        if isinstance(value, str):
          prop_xml.text = value.decode('utf-8')
        else:
          prop_xml.text = str(value)
    #self._getOrderLineDetails(sale_order, root)
    xml = etree.tostring(root, pretty_print=True)
    #order_xml = etree.tostring(order, pretty_print=True)
    #self.validateXMLScheme(order_xml, "SaleOrder.xsd")
    #LOG("returning xml", 300, "\n%s" %(xml))
    return "", xml

  def getSaleOrderLineCategoryList(self, *args, **kw):
    if not kw.has_key('sale_order_id'):
      raise ValueError("No parameter sale_order_id given, got %s / %s" %(args, kw))
    sale_order_id = kw['sale_order_id']
    # retrieve the sale order from the test module
    sale_order_list = self.context.getPortalObject().virtuemart_test_module.searchFolder(id=sale_order_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Virtuemart Test Sale Order")
    if len(sale_order_list) != 1:
      raise KeyError(sale_order_id)
    else:
      sale_order = sale_order_list[0].getObject()
    #LOG("Viewing sale_order", INFO, "sale_order: %s" %(sale_order))
    if not kw.has_key('sale_order_line_id'):
      raise ValueError("No parameter sale_order_line_id given, got %s / %s" %(args, kw))
    sale_order_line_id = kw['sale_order_line_id']
    # retrieve the resource from the test module
    resource_list = sale_order.searchFolder(id=sale_order_line_id, validation_state="validated",
                                            portal_type="Virtuemart Test Sale Order Item")
    if len(resource_list) != 1:
      raise KeyError(sale_order_line_id)
    else:
      resource = resource_list[0].getObject()
    LOG("Viewing sale_order line", INFO, "sale_order_line: %s" %(resource))
    variation_list = resource.searchFolder(validation_state="validated",
                                           portal_type='Virtuemart Test Product Variation')
    
    root = self.generateResultHeader()
    for attribute in variation_list:
      attribute = attribute.getObject()
      variation = etree.SubElement(root, "object")  
      prop_xml = etree.SubElement(variation, "id")
      prop_xml.text = str(attribute.getId())
      prop_xml = etree.SubElement(variation, "category")
      value = attribute.getCategory()
      if isinstance(value, str):
        prop_xml.text = value.decode('utf-8')
      else:
        prop_xml.text = str(value)
    xml = etree.tostring(root, pretty_print=True)
    #LOG("Viewing xml", INFO, "xml: %s" %(xml))
    return "", xml

