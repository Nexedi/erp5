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

UBERCART_XSD_PATH="portal_skins/erp5_tiosafe_ubercart_test/XSD/"

ORDER_PROPERTY_DEFINITION = (
        'id',
        'start_date',
        'reference',
        'currency',
        'billing_first_name',
        'billing_last_name',
        'billing_company',
        'billing_country',
        'delivery_first_name',
        'delivery_last_name',
        'delivery_company',
        'delivery_country',
        'payment_method',
        'primary_email',
        'delivery_title',
        'delivery_price',
        'delivery_tax_rate',
        'discount_code',
        'discount_title',
        'discount_price',
        'discount_tax_rate',
        'order_total',
) 

ORDER_LINE_PROPERTY_DEFINITION = (
        'id',
        'reference',
        'id_product',
        'title',
        'quantity',
        'currency',
        'price',
        'net_price',
        'vat',
        'vat_price',
)

PERSON_PROPERTY_DEFINITION = (
        'id',
        'reference',
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
        'state',
)

PRODUCT_CATEGORY_PROPERTY_DEFINITION = (
        'id',
        'category',
        'distinction',
)

class UbercartTestConnector:

  def __init__(self):
    """
    """
    from Products.ERP5.ERP5Site import getSite
    self.context = getSite()

  def validateXMLScheme(self, xml, xsd_filename):
    """
    Validate generated xml agains XSD provided by ubercart
    """
    xsd = self.context.restrictedTraverse(UBERCART_XSD_PATH+xsd_filename)
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

  def getPropertySheetDefinitionList(self, type):
    definition_dict = {"product" : PRODUCT_PROPERTY_DEFINITION,
                       "product_category" : PRODUCT_CATEGORY_PROPERTY_DEFINITION,
                       "person" : PERSON_PROPERTY_DEFINITION,
                       "order" : ORDER_PROPERTY_DEFINITION,
                       "order_line" : ORDER_LINE_PROPERTY_DEFINITION}
    return definition_dict[type]

  def getDeliveredPersonList(self, *args, **kw):
    person_list = self.context.getPortalObject().ubercart_test_module.searchFolder(portal_type="Ubercart Test Delivery Person",
                                                                                   validation_state="validated")
    root = self.generateResultHeader()
    # must put date into product_list
    for person in person_list:
      person = person.getObject()
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

  def getPersonList(self, *args, **kw):
    person_list = self.context.getPortalObject().ubercart_test_module.searchFolder(portal_type="Ubercart Test Person",
                                                                                   validation_state="validated")
    root = self.generateResultHeader()
    # must put date into product_list
    for person in person_list:
      person = person.getObject()
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

  def getPerson(self, *args, **kw):
    if not kw.has_key('person_id'):
      raise ValueError("No parameter person_id passed to PersonGet, got %s / %s" %(args, kw))
    person_id = kw["person_id"]
    # retrieve the person inside the test module
    person_list = self.context.getPortalObject().ubercart_test_module.searchFolder(id=person_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Ubercart Test Person")
    if len(person_list) != 1:
      raise KeyError(person_id)
    else:
      person_object = person_list[0].getObject()
    root = self.generateResultHeader()
    # Data part
    person_element = etree.SubElement(root, "object")      
    for prop in self.getPropertySheetDefinitionList("person"):
      prop_xml = etree.SubElement(person_element, prop)
      value = getattr(aq_base(person_object), prop, "")
      if isinstance(value, str):
        prop_xml.text = value.decode('utf-8')
      else:
        prop_xml.text = str(value)

    xml = etree.tostring(root, pretty_print=True)
    #person_xml = etree.tostring(person, pretty_print=True)
    #self.validateXMLScheme(person_xml, "Person.xsd")
    return "", xml

  def getDeliveredPerson(self, *args, **kw):
    if not kw.has_key('person_id'):
      raise ValueError("No parameter person_id passed to PersonGet, got %s / %s" %(args, kw))
    person_id = kw["person_id"]
    # retrieve the person inside the test module
    person_list = self.context.getPortalObject().ubercart_test_module.searchFolder(id=person_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Ubercart Test Delivery Person")
    if len(person_list) != 1:
      raise KeyError(person_id)
    else:
      person_object = person_list[0].getObject()
    root = self.generateResultHeader()
    # Data part
    person_element = etree.SubElement(root, "object")      
    for prop in self.getPropertySheetDefinitionList("person"):
      prop_xml = etree.SubElement(person_element, prop)
      value = getattr(aq_base(person_object), prop, "")
      if isinstance(value, str):
        prop_xml.text = value.decode('utf-8')
      else:
        prop_xml.text = str(value)

    xml = etree.tostring(root, pretty_print=True)
    #person_xml = etree.tostring(person, pretty_print=True)
    #self.validateXMLScheme(person_xml, "Person.xsd")
    return "", xml

  def getPersonAddressList(self, *args, **kw):
    if kw.has_key('id') and not kw.has_key('person_id'):
       kw["person_id"] = kw["id"]
    if not kw.has_key('person_id'):
      raise ValueError("No parameter person_id passed to PersonGet, got %s / %s" %(args, kw))
    person_id = kw["person_id"]
    # retrieve the person inside the test module
    person_list = self.context.getPortalObject().ubercart_test_module.searchFolder(id=person_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Ubercart Test Person")
    if len(person_list) == 0:
      raise KeyError(person_id)
    else:
      person_object = person_list[0].getObject()
    root = self.generateResultHeader()
    # Data part
    address_element = etree.SubElement(root, "object")      
    
    for prop in ["id","street", "zip", "city", "country"]:
      prop_xml = etree.SubElement(address_element, prop)
      value = getattr(aq_base(person_object), prop, "")
      if isinstance(value, str):
        prop_xml.text = value.decode('utf-8')
      else:
        prop_xml.text = str(value)

    xml = etree.tostring(root, pretty_print=True)
    #person_xml = etree.tostring(person, pretty_print=True)
    #self.validateXMLScheme(person_xml, "Person.xsd")
    return "", xml

  def getDeliveredPersonAddressList(self, *args, **kw):
    if kw.has_key('id') and not kw.has_key('person_id'):
       kw["person_id"] = kw["id"]
    if not kw.has_key('person_id'):
      raise ValueError("No parameter person_id passed to PersonGet, got %s / %s" %(args, kw))
    person_id = kw["person_id"]
    # retrieve the person inside the test module
    person_list = self.context.getPortalObject().ubercart_test_module.searchFolder(id=person_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Ubercart Test Delivery Person")
    if len(person_list) == 0:
      raise KeyError(person_id)
    else:
      person_object = person_list[0].getObject()
    root = self.generateResultHeader()
    # Data part
    address_element = etree.SubElement(root, "object")      
    
    for prop in ["id","street", "zip", "city", "country"]:
      prop_xml = etree.SubElement(address_element, prop)
      value = getattr(aq_base(person_object), prop, "")
      if isinstance(value, str):
        prop_xml.text = value.decode('utf-8')
      else:
        prop_xml.text = str(value)

    xml = etree.tostring(root, pretty_print=True)
    #person_xml = etree.tostring(person, pretty_print=True)
    #self.validateXMLScheme(person_xml, "Person.xsd")
    return "", xml


  def getOrganisationList(self, *args, **kw):
    org_list = self.context.getPortalObject().ubercart_test_module.searchFolder(portal_type="Ubercart Test Person",
                                                                                validation_state="validated")
    root = self.generateResultHeader()
    # must put date into organisation_list
    organisation_list = organisation_gid_list = []
    for organisation in org_list:
      organisation = organisation.getObject()
      org_id = getattr(aq_base(organisation), "company", "")
      country = getattr(aq_base(organisation), "country", "")
      if org_id in [None, "None"]:
        org_id = ""
      if country in [None, "None"]:
        country = ""
      gid = "%s %s" % (org_id, country)
      if org_id != "" and gid.replace(" ","") != "" and gid not in organisation_gid_list:
        organisation_list.append(organisation)
        organisation_gid_list.append(gid)

    for organisation in organisation_list:
      organisation_id = getattr(aq_base(organisation), "company", "")
      # we got an organisation inside the person 
      organisation_element = etree.SubElement(root, "object")
      for prop in ["company","id","email","street","zip","city","country","country_name"]:
        if prop == "company":
          value = getattr(aq_base(organisation), prop, "")
          prop_xml = etree.SubElement(organisation_element, "billing_company")
        elif prop == "email":
          value = getattr(aq_base(organisation), prop, "")
          prop_xml = etree.SubElement(organisation_element, "primary_email")
        elif prop == "country_name":
          value = getattr(aq_base(organisation), "country", "")
          prop_xml = etree.SubElement(organisation_element, "country")
        elif prop == "street":
          value = getattr(aq_base(organisation), "street", "")
          prop_xml = etree.SubElement(organisation_element, "billing_street1")
        else:
          value = getattr(aq_base(organisation), prop, "")
          if prop == "id":
            prop_xml = etree.SubElement(organisation_element, prop)
          else:
            prop_xml = etree.SubElement(organisation_element, "billing_%s" % prop)
        if isinstance(value, str):
          prop_xml.text = value.decode('utf-8')
        else:
          prop_xml.text = str(value)

    xml = etree.tostring(root, pretty_print=True)
    #persons_xml = etree.tostring(root, pretty_print=True)
    #self.validateXMLScheme(persons_xml, "PersonList.xsd")
    return "", xml

  def getOrganisation(self, *args, **kw):
    if not kw.has_key('organisation_id'):
      raise ValueError("No parameter organisation_id passed to getOrganisation, got %s / %s" %(args, kw))
    organisation_id = kw["organisation_id"]
    # retrieve the organisation inside the test module
    org_list = self.context.getPortalObject().ubercart_test_module.searchFolder(id=organisation_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Ubercart Test Person")
    organisation_list = organisation_gid_list = []
    for organisation in org_list:
      organisation = organisation.getObject()
      org_id = getattr(aq_base(organisation), "company", "")
      country = getattr(aq_base(organisation), "country", "")
      if org_id in [None, "None"]:
        org_id = ""
      if country in [None, "None"]:
        country = ""
      gid = "%s %s" % (org_id, country)
      if org_id != "" and org_id != "None" and gid.replace(" ","") != "" and gid not in organisation_gid_list:
        organisation_list.append(organisation)
        organisation_gid_list.append(gid)

    if len(organisation_list) < 1:
      raise KeyError(organisation_id)
    else:
      organisation = organisation_list[0]
    root = self.generateResultHeader()
    # Data part
    organisation_id = getattr(aq_base(organisation), "company", "")
    if organisation_id != "":
      # we got an organisation inside the person 
      organisation_element = etree.SubElement(root, "object")
      for prop in ["company","id","email","street","zip","city","country","country_name"]:
        if prop == "company":
          value = getattr(aq_base(organisation), prop, "")
          prop_xml = etree.SubElement(organisation_element, "billing_company")
        elif prop == "email":
          value = getattr(aq_base(organisation), prop, "")
          prop_xml = etree.SubElement(organisation_element, "primary_email")
        elif prop == "country_name":
          value = getattr(aq_base(organisation), "country", "")
          prop_xml = etree.SubElement(organisation_element, "country")
        elif prop == "street":
          value = getattr(aq_base(organisation), "street", "")
          prop_xml = etree.SubElement(organisation_element, "billing_street1")
        else:
          value = getattr(aq_base(organisation), prop, "")
          if prop == "id":
            prop_xml = etree.SubElement(organisation_element, prop)
          else:
            prop_xml = etree.SubElement(organisation_element, "billing_%s" % prop)
        if isinstance(value, str):
          prop_xml.text = value.decode('utf-8')
        else:
          prop_xml.text = str(value)

    xml = etree.tostring(root, pretty_print=True)
    #person_xml = etree.tostring(person, pretty_print=True)
    #self.validateXMLScheme(product_xml, "Person.xsd")
    return "", xml

  def getDeliveryOrganisationList(self, *args, **kw):
    org_list = self.context.getPortalObject().ubercart_test_module.searchFolder(portal_type="Ubercart Test Delivery Person",
                                                                                validation_state="validated")
    root = self.generateResultHeader()
    # must put date into organisation_list
    organisation_list = []
    organisation_gid_list = []
    for organisation in org_list:
      organisation = organisation.getObject()
      org_id = getattr(aq_base(organisation), "company", "")
      country = getattr(aq_base(organisation), "country", "")
      if org_id  in [None, "None"]:
        org_id = ""
      if country in [None, "None"]:
        country = ""
      gid = "%s %s" % (org_id, country)
      if org_id != "" and gid.replace(" ","") != "" and gid not in organisation_gid_list:
        organisation_list.append(organisation)
        organisation_gid_list.append(gid)

    for organisation in organisation_list:
      organisation_id = getattr(aq_base(organisation), "company", "")
      # we got an organisation inside the person 
      organisation_element = etree.SubElement(root, "object")
      for prop in ["company","id","email","street","zip","city","country","country_name"]:
        if prop == "company":
          value = getattr(aq_base(organisation), prop, "")
          prop_xml = etree.SubElement(organisation_element, "delivery_company")
        elif prop == "email":
          value = getattr(aq_base(organisation), prop, "")
          prop_xml = etree.SubElement(organisation_element, "primary_email")
        elif prop == "country_name":
          value = getattr(aq_base(organisation), "country", "")
          prop_xml = etree.SubElement(organisation_element, "country")
        elif prop == "street":
          value = getattr(aq_base(organisation), "street", "")
          prop_xml = etree.SubElement(organisation_element, "delivery_street1")
        else:
          value = getattr(aq_base(organisation), prop, "")
          if prop == "id":
            prop_xml = etree.SubElement(organisation_element, prop)
          else:
            prop_xml = etree.SubElement(organisation_element, "delivery_%s" % prop)
        if isinstance(value, str):
          prop_xml.text = value.decode('utf-8')
        else:
          prop_xml.text = str(value)

    xml = etree.tostring(root, pretty_print=True)
    #persons_xml = etree.tostring(root, pretty_print=True)
    #self.validateXMLScheme(persons_xml, "PersonList.xsd")
    return "", xml

  def getDeliveryOrganisation(self, *args, **kw):
    if not kw.has_key('organisation_id'):
      raise ValueError("No parameter organisation_id passed to getOrganisation, got %s / %s" %(args, kw))
    organisation_id = kw["organisation_id"]
    # retrieve the organisation inside the test module
    org_list = self.context.getPortalObject().ubercart_test_module.searchFolder(id=organisation_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Ubercart Test Delivery Person")
    organisation_list = organisation_gid_list = []
    for organisation in org_list:
      organisation = organisation.getObject()
      org_id = getattr(aq_base(organisation), "company", "")
      country = getattr(aq_base(organisation), "country", "")
      if org_id in [None, "None"]:
        org_id = ""
      if country in [None, "None"]:
        country = ""
      gid = "%s %s" % (org_id, country)
      if org_id != "" and gid.replace(" ","") != ""  and gid not in organisation_gid_list:
        organisation_list.append(organisation)
        organisation_gid_list.append(gid)

    if len(organisation_list) < 1:
      raise KeyError(organisation_id)
    else:
      organisation = organisation_list[0]
    root = self.generateResultHeader()
    # Data part
    organisation_id = getattr(aq_base(organisation), "company", "")
    if organisation_id != "":
      # we got an organisation inside the person 
      organisation_element = etree.SubElement(root, "object")
      for prop in ["company","id","email","street","zip","city","country","country_name"]:
        if prop == "company":
          value = getattr(aq_base(organisation), prop, "")
          prop_xml = etree.SubElement(organisation_element, "delivery_company")
        elif prop == "email":
          value = getattr(aq_base(organisation), prop, "")
          prop_xml = etree.SubElement(organisation_element, "primary_email")
        elif prop == "country_name":
          value = getattr(aq_base(organisation), "country", "")
          prop_xml = etree.SubElement(organisation_element, "country")
        elif prop == "street":
          value = getattr(aq_base(organisation), "street", "")
          prop_xml = etree.SubElement(organisation_element, "delivery_street1")
        else:
          value = getattr(aq_base(organisation), prop, "")
          if prop == "id":
            prop_xml = etree.SubElement(organisation_element, prop)
          else:
            prop_xml = etree.SubElement(organisation_element, "delivery_%s" % prop)
        if isinstance(value, str):
          prop_xml.text = value.decode('utf-8')
        else:
          prop_xml.text = str(value)

    xml = etree.tostring(root, pretty_print=True)
    #person_xml = etree.tostring(person, pretty_print=True)
    #self.validateXMLScheme(product_xml, "Person.xsd")
    return "", xml

  #def getPropertySheetDefinitionList(self, object):
    #from Products.ERP5Type import interfaces, Constraint, Permissions, PropertySheet
    #prop_list = []
    #for property_sheet_name in object.getTypeInfo().getTypePropertySheetList():
      #if "Ubercart" in property_sheet_name:
        #base = getattr(PropertySheet, property_sheet_name, None)
        #if base is not None:
          #prop_list = [x['id'] for x in base._properties]
    #return prop_list

  def updatePerson(self, *args, **kw):
    if not kw.has_key('person_id'):
      raise ValueError("No parameter person_id passed to PersonGet, got %s / %s" %(args, kw))
    person_id = kw["person_id"]
    # retrieve the person inside the test module
    person_list = self.context.getPortalObject().ubercart_test_module.searchFolder(id=person_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Ubercart Test Person")
    if len(person_list) != 1:
      raise KeyError(person_id)
    else:
      person = person_list[0].getObject()
    root = self.generateResultHeader()
    person_dict = {}
    for key in kw.keys():
      if key not in ["start_date", "stop_date", "person_id"]:
        person_dict[key] = kw[key]

    LOG("editing person %s with %s" %(person.getPath(), person_dict,), 300, "\n")
    person.edit(**person_dict)
    transaction.commit()
    # Return default xml
    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    return "", xml


  def checkCategoryExistency(self, *args, **kw):
    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    return "", xml

  def getProductCategoryList(self, *args, **kw):
    if not kw.has_key('product_id'):
      raise ValueError("No product_id passed to getProductCategoryList, got %s / %s" %(args, kw))
    resource_id = kw['product_id']
    # retrieve the product inside the test module
    resource_list = self.context.getPortalObject().ubercart_test_module.searchFolder(id=resource_id,
                                                                            portal_type="Ubercart Test Product")
    if len(resource_list) != 1:
      raise KeyError(resource_id)
    else:
      resource = resource_list[0].getObject()
    
    category_list = resource.searchFolder(portal_type="Ubercart Test Product Individual Variation")
    
    root = self.generateResultHeader()
    # must put date into category_list
    for category_object in category_list:
      category_object = category_object.getObject()
      category = etree.SubElement(root, "object")      
      for prop in self.getPropertySheetDefinitionList("product_category"):
        prop_xml = etree.SubElement(category, prop)
        value = getattr(aq_base(category_object), prop, "")
        if isinstance(value, str):
          prop_xml.text = value.decode('utf-8')
        else:
          prop_xml.text = str(value)

    xml = etree.tostring(root, pretty_print=True)
    return "", xml

  def createProductCategory(self, *args, **kw):
    if kw.has_key("id_product"):
      if isinstance(kw['id_product'], unicode):
        kw["product_id"] = kw['id_product'].encode()
      else:
        kw["product_id"] = kw['id_product']
    if not kw.has_key('product_id'):
      raise ValueError("No product_id passed to createProductCategory, got %s / %s" %(args, kw))
    resource_id = kw['product_id']
    if not kw.has_key('base_category'):
      raise ValueError("No base_category passed to createProductCategory, got %s / %s" %(args, kw))
    base_category = kw['base_category']
    if base_category.startswith("'") or base_category.startswith('"'):
       base_category = base_category[1:len(base_category)-1]
    if not kw.has_key('variation'):
      raise ValueError("No variation passed to createProductCategory, got %s / %s" %(args, kw))
    variation = kw['variation']
    if variation.startswith("'") or variation.startswith('"'):
       variation= variation[1:len(variation)-1]

    # retrieve the product inside the test module
    resource_list = self.context.getPortalObject().ubercart_test_module.searchFolder(id=resource_id,
                                                                            portal_type="Ubercart Test Product")
    if len(resource_list) != 1:
      raise KeyError(resource_id)
    else:
      resource = resource_list[0].getObject()
    product_category = resource.newContent(portal_type="Ubercart Test Product Individual Variation")
    keywords = {}
    keywords["category"] = "%s/%s" % (base_category, variation)
    keywords["distinction"] =  product_category.getId()
    product_category.edit(**keywords)
    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    return "", xml

  def deleteProductAttributeCombination(self, *args, **kw):
    if kw.has_key("id_product"):
      if isinstance(kw['id_product'], unicode):
        kw["product_id"] = kw['id_product'].encode()
      else:
        kw["product_id"] = kw['id_product']    
    if not kw.has_key('product_id'):
      raise ValueError("No product_id passed to deleteProductCategory, got %s / %s" %(args, kw))
    resource_id = kw['product_id']
    if not kw.has_key('base_category'):
      raise ValueError("No base_category passed to deleteProductCategory, got %s / %s" %(args, kw))
    base_category = kw['base_category']
    if base_category.startswith("'") or base_category.startswith('"'):
       base_category = base_category[1:len(base_category)-1]
    if not kw.has_key('variation'):
      raise ValueError("No variation passed to deleteProductCategory, got %s / %s" %(args, kw))
    variation = kw['variation']
    if variation.startswith("'") or variation.startswith('"'):
       variation= variation[1:len(variation)-1]

    # retrieve the product inside the test module
    resource_list = self.context.getPortalObject().ubercart_test_module.searchFolder(id=resource_id,
                                                                            portal_type="Ubercart Test Product")
    if len(resource_list) != 1:
      raise KeyError(resource_id)
    else:
      resource = resource_list[0].getObject()
    category = "%s/%s" % (base_category, variation)
    category_list = resource.searchFolder(portal_type="Ubercart Test Product Individual Variation")
    list_ids = []
    for category_object in category_list:
      category_object = category_object.getObject()
      if category_object.getCategory() == category:
        list_ids.append(category_object.getId()) 
    if list_ids != []:
      resource.manage_delObjects(list_ids)

    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    return "", xml


  def deleteProductCategory(self, *args, **kw):
    if not kw.has_key('product_id'):
      raise ValueError("No product_id passed to deleteProductCategory, got %s / %s" %(args, kw))
    resource_id = kw['product_id']
    if not kw.has_key('base_category'):
      raise ValueError("No base_category passed to deleteProductCategory, got %s / %s" %(args, kw))
    base_category = kw['base_category']
    if base_category.startswith("'") or base_category.startswith('"'):
       base_category = base_category[1:len(base_category)-1]
    if not kw.has_key('variation'):
      raise ValueError("No variation passed to deleteProductCategory, got %s / %s" %(args, kw))
    variation = kw['variation']
    if variation.startswith("'") or variation.startswith('"'):
       variation= variation[1:len(variation)-1]

    # retrieve the product inside the test module
    resource_list = self.context.getPortalObject().ubercart_test_module.searchFolder(id=resource_id,
                                                                            portal_type="Ubercart Test Product")
    if len(resource_list) != 1:
      raise KeyError(resource_id)
    else:
      resource = resource_list[0].getObject()
    category = "%s/%s" % (base_category, variation)
    category_list = resource.searchFolder(portal_type="Ubercart Test Product Individual Variation")
    list_ids = []
    for category_object in category_list:
      category_object = category_object.getObject()
      if category_object.getCategory() == category:
        list_ids.append(category_object.getId()) 
    if list_ids != []:
      resource.manage_delObjects(list_ids)

    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    return "", xml



  #
  # This is the Product part
  #
  def getProductList(self, *args, **kw):
    resource_list = self.context.getPortalObject().ubercart_test_module.searchFolder(portal_type="Ubercart Test Product",
                                                                                   validation_state="validated")
    root = self.generateResultHeader()
    # must put date into product_list
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

  def getProduct(self, *args, **kw):
    if not kw.has_key('product_id'):
      raise ValueError("No product_id passed to ProductGet, got %s / %s" %(args, kw))
    resource_id = kw['product_id']
    # retrieve the product inside the test module
    resource_list = self.context.getPortalObject().ubercart_test_module.searchFolder(id=resource_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Ubercart Test Product")
    if len(resource_list) != 1:
      raise KeyError(resource_id)
    else:
      resource = resource_list[0].getObject()
    root = self.generateResultHeader()
    # Data part
    product = etree.SubElement(root, "object")
    for prop in self.getPropertySheetDefinitionList("product"):
      prop_xml = etree.SubElement(product, prop)
      value = getattr(aq_base(resource), prop, "")
      if isinstance(value, str):
        prop_xml.text = value.decode('utf-8')
      else:
        prop_xml.text = str(value)
    xml = etree.tostring(root, pretty_print=True)
    #product_xml = etree.tostring(product, pretty_print=True)
    #self.validateXMLScheme(product_xml, "Product.xsd")
    return "", xml

  def getLastProductID(self, *args, **kw):
    resource_list = self.context.getPortalObject().ubercart_test_module.searchFolder(portal_type="Ubercart Test Product")
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



  def createProduct(self, *args, **kw):
    if not kw.has_key('reference'):
      raise ValueError("No reference passed to createProduct, got %s / %s" %(args, kw))
    keywords = {} 
    keywords["reference"] = kw['reference'].strip('"').strip("'")
    if kw.has_key('title'):
      keywords["title"] = kw['title'].strip('"').strip("'")
    if kw.has_key('sale_price'):
      keywords["sale_price"] = kw['sale_price']
    if kw.has_key('  purchase_price'):
      keywords["purchase_price"] = kw['purchase_price']
    resource = self.context.getPortalObject().ubercart_test_module.newContent(portal_type="Ubercart Test Product")
    resource.edit(**keywords)
    resource.validate()
    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    return "", xml


  def deleteProduct(self, *args, **kw):
    if not kw.has_key('product_id'):
      raise ValueError("No product_id passed to deleteProduct, got %s / %s" %(args, kw))
    resource_id = kw['product_id']
    # retrieve the product inside the test module
    resource_list = self.context.getPortalObject().ubercart_test_module.searchFolder(id=resource_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Ubercart Test Product")
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
      raise ValueError("No product_id passed to updateProductName, got %s / %s" %(args, kw))
    if not kw.has_key('title') :
      raise ValueError("No title passed to updateProductName, got %s / %s" %(args, kw))
    title = kw['title']
    resource_id = kw['product_id']
    # retrieve the product inside the test module
    resource_list = self.context.getPortalObject().ubercart_test_module.searchFolder(id=resource_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Ubercart Test Product")
    if len(resource_list) != 1:
      raise KeyError(resource_id)
    else:
      resource = resource_list[0].getObject()
    title = title.strip('"')
    title = title.strip("'")
    resource.edit(title=title)
    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    return "", xml


  #
  # This is the Order part
  #
  def getSaleOrder(self, *args, **kw):
    if not kw.has_key('sale_order_id'):
      raise ValueError("No sale_order_id passed to getSaleOrder, got %s / %s" %(args, kw))
    order_id = kw['sale_order_id']

    sale_order_list = self.context.getPortalObject().ubercart_test_module.searchFolder(id=order_id,
                                                                           portal_type="Ubercart Test Sale Order")
    if len(sale_order_list) != 1:
      raise KeyError(order_id)
    else:
      sale_order = sale_order_list[0].getObject()

    root = self.generateResultHeader()
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


  def getSaleOrderList(self, *args, **kw):
    sale_order_list = self.context.getPortalObject().ubercart_test_module.searchFolder(portal_type="Ubercart Test Sale Order")
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
      raise ValueError("No sale_order_id passed to OrderGetDetails, got %s / %s" %(args, kw))
    sale_order_id = kw['sale_order_id']

    sale_order_list = self.context.getPortalObject().ubercart_test_module.searchFolder(id=sale_order_id,
                                                                 portal_type="Ubercart Test Sale Order")
    if len(sale_order_list) != 1:
      raise KeyError(sale_order_id)
    else:
      sale_order_object = sale_order_list[0].getObject()

    # retrieve the order inside the test module
    sale_order_line_list = sale_order_object.searchFolder(portal_type="Ubercart Test Sale Order Item")

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
