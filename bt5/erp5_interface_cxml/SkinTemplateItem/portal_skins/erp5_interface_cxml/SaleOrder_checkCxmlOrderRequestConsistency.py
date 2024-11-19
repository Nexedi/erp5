"""
Check that sale order is consisten with Cxml Order Request
"""
portal = context.getPortalObject()
translate = portal.Base_translateString
error_list = []

if context.getPortalType() == "Sale Packing List":
# Carrier name and Tracking number are mandatory in Ariba
  if context.getDestinationCarrierValue() is None:
    error_list.append("Destination Carrier must be defined")
  if not context.getDestinationReference():
    error_list.append("Tracking Nb must be defined")

if order_request_value is None:
  order_request_value = context.Order_getRelatedOrderRequestValue()

def getOrganisationValueFromNetworkId(network_id):
  network_id_value =portal.portal_catalog.getResultValue(
    portal_type="Network Id",
    reference=network_id)
  if network_id_value is not None:
    return network_id_value.getParentValue()

source_section_value = context.getSourceSectionValue()
if source_section_value is None and fixit:
  source_section_value = getOrganisationValueFromNetworkId(order_request_value.getTo().rstrip("-Test"))
  context.setSourceSectionValue(source_section_value)
if source_section_value is None:
  source_section_network_id = None
else:
  source_section_network_id = source_section_value.getDefaultNetworkIdReference()
if source_section_network_id != order_request_value.getTo().rstrip("-Test"):
  error_list.append(translate(
        "Supplier NetworkId is ${source_section_network_id} but the Order Request defines ${to_network_id}",
        mapping=dict(source_section_network_id=source_section_network_id, to_network_id=order_request_value.getTo().rstrip("-Test"))
      ))

destination_section_value = context.getDestinationSectionValue()
#if destination_section_value is None and fixit:
#  destination_section_value = getOrganisationValueFromNetworkId(order_request_value.getFrom().rstrip("-Test"))
#  context.setDestinationSectionValue(destination_section_value)
if destination_section_value is None:
  destination_section_network_id = None
else:
  destination_section_network_id = destination_section_value.getDefaultNetworkIdReference()
if destination_section_network_id != order_request_value.getFrom().rstrip("-Test"):
  error_list.append(translate(
        "Client NetworkId is ${destination_section_network_id} but the Order Request defines ${from_network_id}",
        mapping=dict(destination_section_network_id=destination_section_network_id, from_network_id=order_request_value.getFrom().rstrip("-Test"))
      ))

try:
  source_address = context.Delivery_getSourceAddressText()[0]
except AttributeError:
  source_address = None
if source_address is None:
  error_list.append(translate(
        "Sender Address must be defined",
        mapping=dict(destination_section_network_id=destination_section_network_id, from_network_id=order_request_value.getFrom().rstrip("-Test"))
      ))

property_title_dict = {
  "": "",
  "address_extension": "Address Extension",
  "city": "City",
  "corporate_name": "Corportate Name",
  "destination_section": "Client",
  "destination_section_address": "Invoicing Address",
  "destination": "Recipient or Beneficiary",
  "destination_address": "Delivery Address",
  "int_index": "Sort Index",
  "order_date": "Order Date",
  "region_title": "Country",
  "street_address": "Street Address",
  "stop_date": "Delivery Date",
  "zip_code": "Postal Code",
  "default_sale_supply_line_destination_reference": "Customer Reference",
  "resource": "Product or Service",
  "destination_section_vat_code": "Client VAT Code",
  "payment_condition_hs_payment_condition": "Payment Condition",
}

child_category_dict = {
  "payment_condition_hs_payment_condition": "hs_payment_condition",
}

def findCreateOrganisation(organisation_dict, create=False):
  # only use non-empty values for search
  search_kw = {k:v for k,v in organisation_dict.items() if v and k in ('portal_type', 'corporate_name')}
  search_kw['validation_state'] = ('draft', 'validated')
  organisation_value = portal.portal_catalog.getResultValue(**search_kw)
  if organisation_value is None and create:
    organisation_dict['title'] = organisation_dict.get('corporate_name')
    organisation_value = portal.organisation_module.newContent(**organisation_dict)
  if organisation_value is not None:
    return organisation_value.getRelativeUrl()

address_key_tuple = ("address_extension", "street_address", "city", "zip_code", "region_title")
def findCreateAddress(category, address_dict, organisation, create=False):
  wrong_value_list = []
  for address_value in organisation.objectValues(portal_type="Address"):
    # the address is correct if all values are same as in the order request.
    # only for the addressID (int_index), we overwrite with the value from cXML
    for key, value in address_dict.items():
      property_value = address_value.getProperty(key) or ""
      if key != "int_index" and property_value != value:
        wrong_value_list.append((key, value, address_value.getProperty(key), address_value.getRelativeUrl()))
        break
    else:
      return address_value.getRelativeUrl()
  if not create:
    return
  address_dict["title"] = " ".join([address_dict[x] for x in address_key_tuple if address_dict.get(x)])
  address_value = order_request_value.CxmlOrderRequest_createRelatedAddress(organisation, **address_dict)
  return address_value.getRelativeUrl()

def createSaleOrderLine(property_dict):
  try:
    resource_reference = property_dict.pop("resource_reference")
  except KeyError:
    resource_reference = None
  if not resource_reference:
    try:
      reference = property_dict.pop('resource')['default_sale_supply_line_destination_reference']
    except KeyError:
      pass
    else:
      sale_supply_line = portal.portal_catalog.getResultValue(**{
        'portal_type': 'Sale Supply Line',
        'destination_reference': reference,
        'validation_state' : 'validated',
      })
      if sale_supply_line is not None:
        # first try to find line with same client
        #for line in sale_supply_line_list:
        #  if line.getDestinationValue() in (
        #    kw['destination_section_value'],
        #    kw['destination_value']
        #  ):
        #    sale_supply_line = line
        #    break
        # then use line without destination
        #if line is None:
        #  for line in sale_supply_line_list:
        #    if line.getDestinationValue() is None:
        #      sale_supply_line = line
        #      break
        property_dict['resource_value'] = sale_supply_line.getResourceValue()
  else:
    property_dict['resource_value'] = portal.portal_catalog.getResultValue(**{
      'portal_type': ('Product', 'Service'),
      'reference': resource_reference,
      'validation_state' : 'validated',
    })
  property_dict['portal_type'] = 'Sale Order Line'
  context.newContent(**property_dict)

def compare(document, property_dict, context_key='', context_title='', parent_context_title='', set_property=False):
  # sort so that "_address" is checked after "_destination*". This is
  # necessary in fixit case because we need to already know about the
  # organisation before we can find or create its address
  for key, value in sorted(property_dict.items()):
    if context.getCxmlChanges():
      continue
    if context.getPortalType() in ("Sale Packing List", "Sale Invoice Transaction") and key in ('order_date', 'int_index'):
      continue
    if document.getPortalType() == "Invoice Line" and key in ('start_date', 'stop_date'):
      continue
    if context.getPortalType() in ("Sale Order", "Sale Packing List") and key == "destination_section_vat_code":
      continue
    if isinstance(value, dict):
      category = document.getProperty(key)
      if not category:
        if fixit:
          if value.get('portal_type') == 'Organisation':
            document.setProperty(key, findCreateOrganisation(value))
          elif value.get('portal_type') == 'Address' and key.endswith("_address"):
            organisation = document.getProperty(key[:-8])
            if organisation is not None:
              document.setProperty(key, findCreateAddress(key, value, context.restrictedTraverse(organisation), create=True))
        else:
          title = translate(property_title_dict.get(key, key))
          if not context_title:
            context_title = translate(property_title_dict.get(context_key, context_key))
          error_list.append(translate(
            '${context} ${key} is not defined."',
            mapping=dict(context=context_title, key=title)
          ))
      else:
        category_value = portal.restrictedTraverse(category)
        compare(category_value, value, context_key=key, parent_context_title=context_title)
    else:
      our_value = document.getProperty(key)
      if (our_value or '') != value:
        if set_property:
          document.setProperty(key, value)
        else:
          title = translate(property_title_dict.get(key, key))
          if not context_title:
            context_title = translate(property_title_dict.get(context_key, context_key))
          # display title instead of id if key is a category in consistency message
          if key in document.getBaseCategoryList() or key in child_category_dict:
            if key in child_category_dict:
              key = child_category_dict[key]
            our_value = portal.portal_categories[key].restrictedTraverse(our_value).getTranslatedTitle()
            value =  portal.portal_categories[key].restrictedTraverse(value).getTranslatedTitle()
          error_list.append(translate(
            '${parent_context}${context}${key} is "${our_value}" but the Order Request defines "${value}"',
            mapping=dict(parent_context="%s: " %parent_context_title if parent_context_title else'',
                         context="%s: " %context_title if context_title else'',
                         key=title, our_value=our_value, value=value)
          ))

compare(context, order_request_value.getPropertyDict(), set_property=fixit)
if context.getPortalType() == "Sale Invoice Transaction":
  line_portal_type = "Invoice Line"
else:
  line_portal_type = '%s Line' %context.getPortalType()
line_list = [x for x in context.objectValues(portal_type=line_portal_type, checked_permission="View") if x.getUse() not in ("trade/tax", "trade/discount_service")]
for i, line in enumerate(line_list):
  if line.getIntIndex() is None:
    if fixit:
      line.setIntIndex(i)
    else:
      error_list.append(translate(
        "Sort Index must be defined on all lines."
      ))
      break

# for Sale Packing List and Sale Invoice Transaction also check that int_index is defined on related Sale Order Lines
if context.getPortalType() in ("Sale Packing List", "Sale Invoice Transaction"):
  for i, line in enumerate(line_list):
    if line.DeliveryLine_getOrderLineIntIndex() is None:
      #if fixit:
      #  line.setIntIndex(i)
      #else:
      error_list.append(translate(
        "Sort Index must be defined on all lines of the related Sale Order."
      ))

if line_portal_type == "Sale Order Line":
  index_method = "getIntIndex"
elif line_portal_type in ("Sale Packing List Line", "Invoice Line"):
  index_method = "DeliveryLine_getOrderLineIntIndex"
line_dict = {getattr(line, index_method)(): line for line in line_list}
order_request_line_property_dict =order_request_value.getLinePropertyDict()

# check that all lines in Order Request exist in the Sale Order and compare their properties
for int_index, property_dict in order_request_line_property_dict.items():
  if int_index not in line_dict and context.getPortalType() == "Sale Order":
    if fixit:
      createSaleOrderLine(property_dict)
    else:
      error_list.append(translate(
        "Line No ${int_index} from Order Request is missing.",
        mapping=dict(int_index=int_index)
      ))
  else:
    line = line_dict.get(int_index)
    if line is not None:
      context_title = translate('Line ${int_index}', mapping=dict(int_index=int_index))
      compare(line, property_dict, context_title=context_title, set_property=fixit)

# now check that we do not have additional lines in the Sale Order which are not in the Order Request
for int_index, line in line_dict.items():
  if int_index not in order_request_line_property_dict and line.getQuantity() != 0:
    if fixit:
      if context.getSimulationState() == 'draft':
        context.manage_delObjects([line.getId()])
      else:
        line.setQuantity(0.0)
    else:
      error_list.append(translate(
        "Line No ${int_index} does not exist in Order Request",
        mapping=dict(int_index=int_index)
      ))

return error_list
