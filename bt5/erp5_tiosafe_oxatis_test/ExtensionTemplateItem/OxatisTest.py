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
from zLOG import LOG, ERROR
from Acquisition import aq_base
import transaction 
from DateTime import DateTime

OXATIS_XSD_PATH="portal_skins/erp5_tiosafe_oxatis_test/XSD/"

PRODUCT_PROPERTY_DEFINITION = (
	'ItemSKU',
	'ProductLanguage',
	'OptionValues1',
	'OptionValues2',
	'OptionValues3',
	'OptionTypes1',
	'OptionTypes2',
	'OptionTypes3',
	'ParentItemID',
	'Name',
	'TaxRate',
	'EcotaxTI',
	'ShowInStockNote',
	'ShowStockLevel',
	'DaysToShip',
	'ShowIfOutOfStock',
	'SaleIfOutOfStock',
	'SaleIfOutOfStockScenario',
	'ShowDaysToship',
	'Weight',
	'DimensionHeight',
	'DimensionWidth',
	'DimensionLength',
	'HandlingSurcharge1ST',
	'HandlingSurchargeOthers',
	'ShipPrice',
	'LastUpdateDate',
)

PERSON_PROPERTY_DEFINITION = (
  	'Email',
	'FirstName',
	'LastName',
	'Password',
	'Company',
	'VATNumber',
	'BillingAddress',
	'BillingAddressL1',
	'BillingAddressL2',
	'BillingAddressL3',
	'BillingAddressL4',
	'BillingZipCode',
	'BillingCity',
	'BillingCountryISOCode',
	'BillingCountryName',
	'BillingPhone',
	'BillingCellPhone',
	'BillingFax',
	'ShippingFirstName',
	'ShippingLastName',
	'ShippingCompany',
	'ShippingPhone',
	'ShippingAddress',
	'ShippingAddressL1',
	'ShippingAddressL2',
	'ShippingAddressL3',
	'ShippingAddressL4',
	'ShippingZipCode',
	'ShippingCity',
	'ShippingCountryISOCode',
	'ShippingCountryName',
	'SubscribeToNewletters',
	'CustomerAccount',
)

ORDER_PROPERTY_DEFINITION = (
  	'Date',
	'BillingFirstName',
	'BillingLastName',
	'NetAmountDue',
	'PaymentStatusCode',
	'UserEmail',
	'UserOxID',
	'BillingCompany',
	'BillingAddress',
	'BillingAddressL1',
	'BillingAddressFloor',
	'BillingAddressBuilding',
	'BillingAddressStreet',
	'BillingZipCode',
	'BillingCity',
	'BillingState',
	'BillingCountryISOCode',
	'BillingCountryName',
	'BillingPhone',
	'BillingCellPhone',
	'BillingFax',
	'CompanyVATNumber',
	'ShippingCompany',
	'ShippingFirstName',
	'ShippingLastName',
	'ShippingAddress',
	'ShippingAddressL1',
	'ShippingAddressFloor',
	'ShippingAddressBuilding',
	'ShippingAddressStreet',
	'ShippingAddressOtherInfo',
	'ShippingZipCode',
	'ShippingCity',
	'ShippingState',
	'ShippingCountryISOCode',
	'ShippingCountryName',
	'ShippingPhone',
	'ShippingInfo',
	'VATIncluded',
	'EcoTaxIncluded',
	'SubTotalNet',
	'SubTotalNetDiscounted',
	'GlobalDiscountRate',
	'GlobalDiscountAmount',
	'SubTotalVAT',
	'ShippingID',
	'ShippingMethodName',
	'ShippingTaxRate',
	'ShippingPriceTaxExcl',
	'ShippingPriceTaxIncl',
	'ShippingVATAmount',
	'EcoTaxAmountTaxIncl',
	'TotalWeight',
	'PaymentMethodName',
	'PMProcessorCode',
	'PaymentStatusLastModifiedDate',
	'RemoteIPAddr',
	'SalesRepCode',
	'SpecialInstructions',
	'CurrencyCode',
    )

ORDER_LINE_PROPERTY_DEFINITION = (
  	'ItemOxID',
	'ItemSKU',
	'ItemSKUOriginal',
	'ItemName',
	'Quantity',
	'GrossPrice',
	'GrossAmount',
	'TaxRate',
	'DiscountRate',
	'NetPrice',
	'NetAmount',
	'VATAmount',
	'EcoTaxValueTaxIncl',
)

class OxatisTestConnector:

  def __init__(self):
    """
    """
    from Products.ERP5.ERP5Site import getSite
    self.context = getSite()


  def validateXMLScheme(self, xml, xsd_filename):
    """
    Validate generated xml agains XSD provided by oxatis
    """
    xsd = self.context.restrictedTraverse(OXATIS_XSD_PATH+xsd_filename)
    xml_schema = ''.join(xsd.data)
    xml_schema = StringIO(xml_schema)
    xml_schema = etree.parse(xml_schema)
    xml_schema = etree.XMLSchema(xml_schema)
    xml_element = etree.XML(xml)
    validated = xml_schema.validate(xml_element)
    if validated is False:
      LOG("validateXMLSchema failed with", ERROR, "%s, xsd = %s\nxml = %s\n" %(str(xml_schema.error_log.filter_from_errors()[0]), xsd.data, xml))
    assert validated is True
    return validated

  def generateResultHeader(self):
    # generate xml
    root = etree.Element("DataResultService")
    # Header part
    status_code = etree.SubElement(root, "StatusCode")
    status_code.text = "200"
    status_subcode = etree.SubElement(root, "StatusSubCode")
    status_subcode = "0"
    etree.SubElement(root, "ErrorDetails")
    return root

  def UserGetList(self, *args, **kw):
    person_list = self.context.getPortalObject().oxatis_test_module.searchFolder(portal_type="Oxatis Test Person",
                                                                                 validation_state='validated')
    root = self.generateResultHeader()
    data = etree.SubElement(root, "Data")
    user_list = etree.SubElement(data, "UserList")
    # retrieve the date from given xml
    if not kw.has_key('data'):
      raise ValueError, "No data passed to UserGetList, got %s / %s" %(args, kw)
    # parse the data to retrieve the date
    context = etree.iterparse(StringIO(kw['data']), events=('end',), tag="LatestModifiedDateStart")
    for event, element in context:
      date_start = element.text
    context = etree.iterparse(StringIO(kw['data']), events=('end',), tag="LatestModifiedDateEnd")
    for event, element in context:
      date_end = element.text
    date = etree.SubElement(user_list, 'LatestModifiedDateStart')
    date.text = date_start
    date = etree.SubElement(user_list, 'LatestModifiedDateEnd')
    date.text = date_end
    # must put date into user_list
    users_id = etree.SubElement(data, "UsersID")

    for person in person_list:
      person = person.getObject()
      user_id = etree.SubElement(users_id, "UserID")
      OxID = etree.SubElement(user_id, "OxID")
      OxID.text = person.getReference().decode('utf-8')
      email = etree.SubElement(user_id, "Email")
      email.text = person.getEmail().decode('utf-8')

    xml = etree.tostring(root, pretty_print=True)
    users_xml = etree.tostring(user_list, pretty_print=True)
    self.validateXMLScheme(users_xml, "UserList.xsd")
    #LOG("returning xml", 300, "\n%s" %(xml))
    return "", xml

  def getPropertySheetDefinitionList(self, type):
    definition_dict = {"product" : PRODUCT_PROPERTY_DEFINITION,
                       "person" : PERSON_PROPERTY_DEFINITION,
                       "order" : ORDER_PROPERTY_DEFINITION,
                       "order_line" : ORDER_LINE_PROPERTY_DEFINITION}
    return definition_dict[type]

  def UserUpdate(self, *args, **kw):
    if not kw.has_key('data'):
      raise ValueError, "No data passed to UserGet, got %s / %s" %(args, kw)
    # Must check xml validity here
    # parse the data to retrieve the user id
    context = etree.iterparse(StringIO(kw['data']), events=('end',), tag="OxID")
    for event, element in context:
      user_id = element.text
    # retrieve the person inside the test module
    person_list = self.context.getPortalObject().oxatis_test_module.searchFolder(reference=user_id,
                                                                                 portal_type="Oxatis Test Person")
    if len(person_list) != 1:
      raise KeyError(user_id)
    else:
      person = person_list[0].getObject()
    context = etree.iterparse(StringIO(kw['data']), events=('end',))
    person_dict = {}
    for event, element in context:
      if element.text is None:
        person_dict[element.tag.lower()] = ""
      else:
        person_dict[element.tag.lower()] = element.text
    person_dict.pop('oxid')
    LOG("editing person %s with %s" %(person.getPath(), person_dict,), 300, "\n")
    person.edit(**person_dict)
    transaction.commit()
    # Return default xml
    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    return "", xml


  def UserGet(self, *args, **kw):
    if not kw.has_key('data'):
      raise ValueError, "No data passed to UserGet, got %s / %s" %(args, kw)
    # Must check xml validity here
    # parse the data to retrieve the user id
    context = etree.iterparse(StringIO(kw['data']), events=('end',), tag="OxID")
    for event, element in context:
      user_id = element.text
    # retrieve the person inside the test module
    person_list = self.context.getPortalObject().oxatis_test_module.searchFolder(reference=user_id,
                                                                                 portal_type="Oxatis Test Person")
    if len(person_list) != 1:
      raise KeyError(user_id)
    else:
      person = person_list[0].getObject()
    root = self.generateResultHeader()
    # Data part
    data = etree.SubElement(root, "Data")
    user = etree.SubElement(data, "User")
    prop_xml = etree.SubElement(user, "OxID")
    prop_xml.text = person.getReference()
    for prop in self.getPropertySheetDefinitionList('person'):
      value = getattr(aq_base(person), prop, "")
      if value is None:
        value = ""
      prop_xml = etree.SubElement(user, prop)
      if prop in ['CustomerAccount', 'SubscribeToNewletters']:
        if value == 0:
          value = "false"
        else:
          value = "true"
      prop_xml.text = value.decode('utf-8')

    xml = etree.tostring(root, pretty_print=True)
    user_xml = etree.tostring(user, pretty_print=True)
    self.validateXMLScheme(user_xml, "User.xsd")
    #LOG("returning xml", 300, "\n%s" %(xml))
    return "", xml

  #
  # This is the Product part
  #
  def ProductGetList(self, *args, **kw):
    resource_list = self.context.getPortalObject().oxatis_test_module.searchFolder(portal_type="Oxatis Test Product",
                                                                                   validation_state="validated")
    root = self.generateResultHeader()
    data = etree.SubElement(root, "Data")
    products = etree.SubElement(data, "ProductList")
    # retrieve the date from given xml
    if not kw.has_key('data'):
      raise ValueError, "No data passed to UserGetList, got %s / %s" %(args, kw)
    # parse the data to retrieve the date
    context = etree.iterparse(StringIO(kw['data']), events=('end',), tag="LatestModifiedDateStart")
    for event, element in context:
      date_start = element.text
    context = etree.iterparse(StringIO(kw['data']), events=('end',), tag="LatestModifiedDateEnd")
    for event, element in context:
      date_end = element.text
    date = etree.SubElement(products, 'LatestModifiedDateStart')
    date.text = date_start
    date = etree.SubElement(products, 'LatestModifiedDateEnd')
    date.text = date_end
    # must put date into product_list
    products_id = etree.SubElement(products, "ProductsID")
    for resource in resource_list:
      resource = resource.getObject()
      product_id = etree.SubElement(products_id, "ProductID")
      OxID = etree.SubElement(product_id, "OxID")
      OxID.text = resource.getReference().decode('utf-8')
      ref = etree.SubElement(product_id, "ItemSKU")
      ref.text = getattr(aq_base(resource), 'ItemSKU', "").decode('utf-8')

    xml = etree.tostring(root, pretty_print=True)
    products_xml = etree.tostring(products, pretty_print=True)
    self.validateXMLScheme(products_xml, "ProductList.xsd")

    #LOG("returning xml", 300, "\n%s" %(xml))
    return "", xml

  def ProductGet(self, *args, **kw):
    if not kw.has_key('data'):
      raise ValueError, "No data passed to ProductGet, got %s / %s" %(args, kw)
    # Must check xml validity here
    # parse the data to retrieve the product id
    context = etree.iterparse(StringIO(kw['data']), events=('end',), tag="OxID")
    for event, element in context:
      resource_id = element.text
    # retrieve the product inside the test module
    resource_list = self.context.getPortalObject().oxatis_test_module.searchFolder(reference=resource_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Oxatis Test Product")
    if len(resource_list) != 1:
      raise KeyError(resource_id)
    else:
      resource = resource_list[0].getObject()
    root = self.generateResultHeader()
    # Data part
    data = etree.SubElement(root, "Data")
    product = etree.SubElement(data, "Product")
    prop_xml = etree.SubElement(product, "OxID")
    prop_xml.text = resource.getReference()
    for prop in self.getPropertySheetDefinitionList("product"):
      value = getattr(aq_base(resource), prop, "")
      if prop == "ParentItemID" and not len(value):
        continue
      if prop.startswith("OptionTypes") or prop.startswith("OptionValues"):
        if not len(value):
          value = "0"
        prop_xml = etree.SubElement(product, prop)
        sub_xml = etree.SubElement(prop_xml, "OxID")
        sub_xml.text = str(value)
      else:
        prop_xml = etree.SubElement(product, prop)
        if isinstance(value, str):
          prop_xml.text = value.decode('utf-8')
        else:
          prop_xml.text = str(value)
        if prop == "Name":
          prop_xml = etree.SubElement(product, "Description")
          prop_xml.text = resource.getDescription()

    xml = etree.tostring(root, pretty_print=True)
    #LOG("returning xml", 300, "\n%s" %(xml))
    product_xml = etree.tostring(product, pretty_print=True)
    self.validateXMLScheme(product_xml, "Product.xsd")
    return "", xml


  def ProductDelete(self, *args, **kw):
    if not kw.has_key('data'):
      raise ValueError, "No data passed to ProductGet, got %s / %s" %(args, kw)
    # Must check xml validity here
    # parse the data to retrieve the product id
    context = etree.iterparse(StringIO(kw['data']), events=('end',), tag="OxID")
    for event, element in context:
      resource_id = element.text
    # retrieve the product inside the test module
    resource_list = self.context.getPortalObject().oxatis_test_module.searchFolder(reference=resource_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Oxatis Test Product")
    if len(resource_list) != 1:
      raise KeyError(resource_id)
    else:
      resource = resource_list[0].getObject()
      resource.invalidate()
    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    #LOG("returning xml", 300, "\n%s" %(xml))
    return "", xml

  def ProductUpdateName(self, *args, **kw):
    if not kw.has_key('data'):
      raise ValueError, "No data passed to ProductGet, got %s / %s" %(args, kw)
    # Must check xml validity here
    # parse the data to retrieve the product id
    context = etree.iterparse(StringIO(kw['data']), events=('end',), tag="OxID")
    for event, element in context:
      resource_id = element.text
    # retrieve the product inside the test module
    resource_list = self.context.getPortalObject().oxatis_test_module.searchFolder(reference=resource_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Oxatis Test Product")
    if len(resource_list) != 1:
      raise KeyError(resource_id)
    else:
      resource = resource_list[0].getObject()
    context = etree.iterparse(StringIO(kw['data']), events=('end',), tag="Name")
    for event, element in context:
      name = element.text
    resource.edit(name=name)
    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    #LOG("returning xml", 300, "\n%s" %(xml))
    return "", xml

  def ProductUpdateDescriptions(self, *args, **kw):
    if not kw.has_key('data'):
      raise ValueError, "No data passed to ProductGet, got %s / %s" %(args, kw)
    # Must check xml validity here
    # parse the data to retrieve the product id
    context = etree.iterparse(StringIO(kw['data']), events=('end',), tag="OxID")
    for event, element in context:
      resource_id = element.text
    # retrieve the product inside the test module
    resource_list = self.context.getPortalObject().oxatis_test_module.searchFolder(reference=resource_id,
                                                                                   validation_state="validated",
                                                                                   portal_type="Oxatis Test Product")
    if len(resource_list) != 1:
      raise KeyError(resource_id)
    else:
      resource = resource_list[0].getObject()
    context = etree.iterparse(StringIO(kw['data']), events=('end',), tag="Description")
    for event, element in context:
      desc = element.text
    resource.edit(description=desc)
    root = self.generateResultHeader()
    xml = etree.tostring(root, pretty_print=True)
    #LOG("returning xml", 300, "\n%s" %(xml))
    return "", xml


  #
  # This is the Order part
  #
  def OrderGetList(self, *args, **kw):
    if not kw.has_key('data'):
      raise ValueError, "No data passed to OrderGet, got %s / %s" %(args, kw)
    # Must check xml validity here
    # parse the data to retrieve the order id
    context = etree.iterparse(StringIO(kw['data']), events=('end',), tag="OrderDateStart")
    for event, element in context:
      start_date = DateTime(element.text)
      date_start = element.text
    context = etree.iterparse(StringIO(kw['data']), events=('end',), tag="OrderDateEnd")
    for event, element in context:
      stop_date = DateTime(element.text)
      date_end = element.text
    sale_order_list = self.context.getPortalObject().oxatis_test_module.searchFolder(portal_type="Oxatis Test Sale Order")
    root = self.generateResultHeader()
    data = etree.SubElement(root, "Data")
    orders = etree.SubElement(data, "OrderList")
    setorderdesc = etree.SubElement(orders, "SetOrderDesc")
    setorderdesc.text = "true"
    date = etree.SubElement(orders, 'OrderDateStart')
    date.text = date_start
    date = etree.SubElement(orders, 'OrderDateEnd')
    date.text = date_end
    payment = etree.SubElement(orders, "PaymentStatusCode")
    payment.text = "40"
    # must put date into order_list
    orders_id = etree.SubElement(orders, "OrderIDs")
    for sale_order in sale_order_list:
      sale_order = sale_order.getObject()
      order_date = DateTime(sale_order.getDate())
      if order_date > start_date and order_date < stop_date:
        order_id = etree.SubElement(orders_id, "OrderID")
        OxID = etree.SubElement(order_id, "OxID")
        OxID.text = sale_order.getReference("").decode('utf-8')

    xml = etree.tostring(root, pretty_print=True)
    orders_xml = etree.tostring(orders, pretty_print=True)
    self.validateXMLScheme(orders_xml, "OrderList.xsd")
    #LOG("returning xml", 300, "\n%s" %(xml))
    return "", xml


  def _getOrderLineDetails(self, sale_order, xml):
    items = etree.SubElement(xml, "OrderItems")
    for line in sale_order.contentValues():
      item = etree.SubElement(items, "Item")
      for prop in self.getPropertySheetDefinitionList("order_line"):
        prop_xml = etree.SubElement(item, prop)
        value = getattr(aq_base(line), prop, "")
        prop_xml.text = value.decode('utf-8')


  def OrderGetDetails(self, *args, **kw):
    if not kw.has_key('data'):
      raise ValueError, "No data passed to OrderGet, got %s / %s" %(args, kw)
    # Must check xml validity here
    # parse the data to retrieve the order id
    context = etree.iterparse(StringIO(kw['data']), events=('end',), tag="OxID")
    for event, element in context:
      sale_order_id = element.text
    # retrieve the order inside the test module
    sale_order_list = self.context.getPortalObject().oxatis_test_module.searchFolder(reference=sale_order_id,
                                                                                 portal_type="Oxatis Test Sale Order")
    if len(sale_order_list) != 1:
      raise KeyError(sale_order_id)
    else:
      sale_order = sale_order_list[0].getObject()
    root = self.generateResultHeader()
    # Data part
    data = etree.SubElement(root, "Data")
    order = etree.SubElement(data, "Order")
    prop_xml = etree.SubElement(order, "OxID")
    prop_xml.text = sale_order.getReference()
    for prop in self.getPropertySheetDefinitionList("order"):
      prop_xml = etree.SubElement(order, prop)
      if prop in ("VATIncluded", "EcoTaxIncluded"):
        value = str(getattr(sale_order, "get%s" %(prop.capitalize()))())
        prop_xml.text = value.lower()
      else:
        value = getattr(aq_base(sale_order), prop, "")
        if value is not None:
          prop_xml.text = value.decode('utf-8')
        else:
          prop_xml.text = ""
    self._getOrderLineDetails(sale_order, root)
    xml = etree.tostring(root, pretty_print=True)
    order_xml = etree.tostring(order, pretty_print=True)
    self.validateXMLScheme(order_xml, "Order.xsd")
    #LOG("returning xml", 300, "\n%s" %(xml))
    return "", xml

  def OptionTypesGet(self, *args, **kw):
    # Base category definition
    bc_dict = {"1" : "Couleur",
               "2" : "Taille",
               }
    if not kw.has_key('data'):
      raise ValueError, "No data passed to OptionTypesGet, got %s / %s" %(args, kw)
    # Must check xml validity here
    # parse the data to retrieve the base category id
    context = etree.iterparse(StringIO(kw['data']), events=('end',), tag="OxID")
    for event, element in context:
      base_category_id = element.text

    root = self.generateResultHeader()
    # Data part
    data = etree.SubElement(root, "Data")
    option = etree.SubElement(data, "OptionTypes")
    prop_xml = etree.SubElement(option, "OxID")
    prop_xml.text = base_category_id
    prop_xml = etree.SubElement(option, "Name")
    prop_xml.text = bc_dict[base_category_id]
    xml = etree.tostring(root, pretty_print=True)
    #LOG("returning xml", 300, "\n%s" %(xml))
    return "", xml

  def OptionValuesGet(self, *args, **kw):
    # Base category definition
    c_dict = {"11" : ("BL", "Bleu"),
              "12" : ("RG", "Rouge"),
              "13" : ("NR", "Noir"),
              "21" : ("XL", "Grande"),
              "22" : ("L", "Large"),
              "23" : ("S", "Petite"),
              }
    if not kw.has_key('data'):
      raise ValueError, "No data passed to OptionsValuesGet, got %s / %s" %(args, kw)
    # Must check xml validity here
    # parse the data to retrieve the base category id
    context = etree.iterparse(StringIO(kw['data']), events=('end',), tag="OxID")
    for event, element in context:
      category_id = element.text

    root = self.generateResultHeader()
    # Data part
    data = etree.SubElement(root, "Data")
    option = etree.SubElement(data, "OptionValues")
    prop_xml = etree.SubElement(option, "OxID")
    prop_xml.text = category_id
    prop_xml = etree.SubElement(option, "Code")
    prop_xml.text = c_dict[category_id][0]
    prop_xml = etree.SubElement(option, "Name")
    prop_xml.text = c_dict[category_id][1]
    xml = etree.tostring(root, pretty_print=True)
    #LOG("returning xml", 300, "\n%s" %(xml))
    return "", xml
  
