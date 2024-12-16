##############################################################################
#
# Copyright (c) 2024 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly advised to contract a Free Software
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from lxml import etree
from erp5.component.document.CxmlDocument import CxmlDocument
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ERP5Type.Permissions import AccessContentsInformation

hs_payment_condition_mapping_dict = {
  "4060": "60E",
  "1030": "N30",
}

def s(u):
  if isinstance(u, unicode):
    return u.encode('utf-8')
  return u

def get_attr(et, tag_name, attr):
  tag = et.find(tag_name)
  if tag is not None:
    return s(tag.get(attr))
  return ''

def get_text(et, tag_name):
  tag = et.find(tag_name)
  if tag is not None:
    return s(tag.text)
  return ''

class CxmlOrderRequest(CxmlDocument):
  meta_type = 'ERP5 Cxml Order Request'
  portal_type = 'Cxml Order Request'

  security = ClassSecurityInfo()
  security.declareObjectProtected(AccessContentsInformation)

  security.declareProtected(AccessContentsInformation, 'getReference')
  def getReference(self):
    et = self.getElementTree()
    if et is None:
      return
    order_request_header = et.xpath('/cXML/Request/OrderRequest/OrderRequestHeader')[0]
    return order_request_header.get('orderID')

  security.declareProtected(AccessContentsInformation, 'getVersion')
  def getVersion(self):
    et = self.getElementTree()
    if et is None:
      return
    order_request_header = et.xpath('/cXML/Request/OrderRequest/OrderRequestHeader')[0]
    return order_request_header.get('orderVersion')

  def _getRegionCategoryForIsoCountryCode(self, iso_country_code):
    portal = self.getPortalObject()
    region_dict = {x.getReference(): x.getRelativeUrl() for x in [portal.portal_categories.region.europe.western_europe.germany] + \
      portal.portal_categories.region.getCategoryChildValueList(include_if_child=0) \
        if not x.getRelativeUrl().startswith('region/europe/western_europe/germany/')}
    return region_dict[iso_country_code]

  def _getAddressPropertyDict(self, address, corporate_name='', name_on_address=''):
    portal = self.getPortalObject()
    postal_address = address.find('PostalAddress')
    iso_country_code = postal_address.find('Country').get('isoCountryCode')
    region = self._getRegionCategoryForIsoCountryCode(iso_country_code)
    region_value = portal.portal_categories.region.unrestrictedTraverse(region)
    address_extension = ''
    if name_on_address and name_on_address != corporate_name:
      address_extension = name_on_address
      if address_extension.startswith(corporate_name):
        address_extension = address_extension[len(corporate_name):].strip()
    deliver_to = get_text(postal_address, 'DeliverTo')
    if deliver_to != corporate_name and deliver_to != address_extension:
      address_extension = ', '.join([x for x in (address_extension, deliver_to) if x])
    property_dict = {
      "portal_type": "Address",
      "street_address": get_text(postal_address, 'Street'),
      "city": get_text(postal_address, 'City'),
      "zip_code": get_text(postal_address, 'PostalCode'),
      "region_title": region_value.getTitle(),
      "address_extension": address_extension}
    int_index = address.get('addressID')
    if int_index is not None:
      property_dict['int_index'] = int(int_index)
    return property_dict

  security.declareProtected(AccessContentsInformation, 'getPropertyDict')
  def getPropertyDict(self):
    """
    Get Sale Order properties and values from OrderRequest cXML
    """
    self.validateXML()
    et = self.getElementTree()
    property_dict = {}
    order_request_header = et.xpath('/cXML/Request/OrderRequest/OrderRequestHeader')[0]
    for terms_of_delivery in order_request_header.findall('TermsOfDelivery'):
      if get_attr(terms_of_delivery, 'TermsOfDeliveryCode', 'value') == 'TransportCondition':
        incoterm = get_attr(terms_of_delivery, 'TransportTerms', 'value')
        if incoterm:
          property_dict['incoterm'] = incoterm.lower()
          break
    for extrinsic in order_request_header.findall("Extrinsic"):
      if extrinsic.get("name") == "Payment Term":
        payment_term = extrinsic.text
        try:
          hs_payment_condition_id = hs_payment_condition_mapping_dict[payment_term]
        except KeyError:
          raise KeyError("No Paymnet Condition Mapping found for Payment Term %s" %payment_term)
        property_dict['payment_condition_hs_payment_condition'] = hs_payment_condition_id
        break
    bill_to = order_request_header.find('BillTo')
    address = bill_to.find('Address')
    bill_to_name = get_text(address, 'Name')
    sold_to_name = s(''.join(order_request_header.xpath('//BusinessPartner[@role="soldTo"]/Address/Name/text()')))
    buyer_vat_id = s(''.join(order_request_header.xpath('//Extrinsic[@name="buyerVatID"]/text()')))
    property_dict['destination_section'] = {'portal_type': 'Organisation', 'corporate_name': sold_to_name or bill_to_name}
    if buyer_vat_id:
      property_dict['destination_section_vat_code'] = buyer_vat_id
    property_dict['destination_section_address'] = self._getAddressPropertyDict(address, corporate_name=sold_to_name or bill_to_name, name_on_address=bill_to_name)
    property_dict['order_date'] = DateTime(order_request_header.get('orderDate'))
    ship_to = order_request_header.find('ShipTo')
    address = ship_to.find('Address')
    name = s(address.find('Name').text)
    property_dict['destination'] = {'portal_type': 'Organisation','corporate_name': name}
    property_dict['destination_address'] = self._getAddressPropertyDict(address, corporate_name=name)
    return property_dict

  security.declareProtected(AccessContentsInformation, 'getLinePropertyDict')
  def getLinePropertyDict(self):
    """
    Get Sale Order Line properties and values from OrderRequest cXML
    """
    portal = self.getPortalObject()
    self.validateXML()
    et = self.getElementTree()
    line_dict = {}
    price_currency_value = None
    for item_out in et.xpath('/cXML/Request/OrderRequest/ItemOut'):
      # We do not support different destination per line
      assert item_out.find('ShipTo') is None
      property_dict = {}
      property_dict['int_index'] = int_index = int(item_out.get("lineNumber"))
      stop_date = item_out.get("requestedDeliveryDate")
      if stop_date is not None:
        property_dict['stop_date'] = DateTime(stop_date)#.toZone('UTC').earliestTime()
      property_dict['quantity'] = float(item_out.get("quantity"))
      item_detail = item_out.find('ItemDetail')
      if item_detail is not None:
        description = item_detail.find('Description')
        if description is not None:
          short_name = description.find('ShortName')
          if short_name is not None:
            property_dict['title'] = s(short_name.text)
            #property_dict['description'] = s(short_name.tail)
          else:
            property_dict['title'] = s(description.text)
            #property_dict['description'] = s(description.text)
        unit_of_measure_text = get_text(item_detail, 'UnitOfMeasure')
        assert unit_of_measure_text in ("EA", "PC")
      property_dict['quantity_unit'] = "unit/piece"
      unit_price = item_detail.find('UnitPrice')
      if unit_price is not None:
        money = unit_price.find('Money')
        if money is not None:
          currency = money.get('currency')
          if currency is not None:
            if price_currency_value is None:
              assert currency in ("EUR", "USD")
              price_currency_value = portal.currency_module[currency]
            else:
              assert price_currency_value.getId() == currency
        property_dict['price'] = float(money.text)
      item_id = item_out.find('ItemID')
      supplier_part_id = get_text(item_id, "SupplierPartID")
      buyer_part_id = get_text(item_id, "BuyerPartID")
      if supplier_part_id:
        property_dict['resource_reference'] = supplier_part_id
      elif buyer_part_id:
        property_dict['resource'] = {'default_sale_supply_line_destination_reference': buyer_part_id}
      line_dict[int_index] = property_dict
    return line_dict

  security.declareProtected(AccessContentsInformation, 'getAribaAttachmentUrl')
  def getAribaAttachmentUrl(self):
    """Get From value from cXML content"""
    et = self.getElementTree()
    el = et.xpath('/cXML/Request/OrderRequest/OrderRequestHeader/Extrinsic[@name="AttachmentOnline"]')
    if len(el):
      return el[0].text

  security.declareProtected(AccessContentsInformation, 'getBuyer')
  def getBuyer(self):
    """Get buyer name from cXML content"""
    et = self.getElementTree()
    return ''.join(et.xpath('/cXML/Request/OrderRequest/OrderRequestHeader/Extrinsic[@name="Buyer"]/text()'))

  security.declareProtected(AccessContentsInformation, 'getDeploymentMode')
  def getDeploymentMode(self):
    """Get deployment mode (test or production) form cXML content"""
    et = self.getElementTree()
    return ''.join(et.xpath('/cXML/Request/@deploymentMode'))

  security.declareProtected(AccessContentsInformation, 'getContactSoldToXml')
  def getContactSoldToXml(self):
    """
    Get Sale Order Line properties and values from OrderRequest cXML
    """
    el_list = self.getElementTree().xpath('/cXML/Request/OrderRequest/OrderRequestHeader/BusinessPartner[@role="soldTo"]/Address')
    if len(el_list):
      address = el_list[0]
      contact = etree.Element("Contact")
      contact.set("role", "soldTo")
      if address.get("addressID"):
        contact.set("addressID", address.get("addressID"))
      for el in address.xpath('Name | PostalAddress'):
        contact.append(el)
      return etree.tostring(contact)
    return  ''

  def process(self):
    portal = self.getPortalObject()
    self.validateXML()
    # we process only orders with orderID
    destination_reference = self.getReference()
    if not destination_reference:
      return
    # try to attach to existing sale order
    sale_order_list = portal.portal_catalog(
      portal_type="Sale Order",
      destination_reference=destination_reference,
      simulation_state = ('draft', 'planned', 'ordered', 'building', 'confirmed'))
    # if we have more than one sale order, let the user decide
    if len(sale_order_list) > 1:
      return
    if len(sale_order_list) == 1:
      sale_order = sale_order_list[0]
      self.setFollowUpValue(sale_order)
      #portal.portal_workflow.doActionFor(self, "validate_action")
