"""
  This script just returns what the user entered in
  the fast input form, searches for the product whose
  reference or title has been just entered and updates
  the total price and the stock corresponding to the 
  product
"""
no_inventory = False

# Check that the requested quantities does not exceed available inventory.
# We only enforce this check for sales.
check_stock_availability = False

portal = context.getPortalObject()
Base_translateString = portal.Base_translateString

delivery = context
if delivery.getPortalType() in portal.getPortalContainerTypeList():
  delivery = context.getExplanationValue()

# Retrieve lines portal type
line_portal_type_list = [x for x in delivery.getTypeInfo().getTypeAllowedContentTypeList() \
                         if x in portal.getPortalMovementTypeList()]
line_portal_type = line_portal_type_list[0]

if line_portal_type in portal.getPortalSaleTypeList():
  section_uid = delivery.getSourceSectionUid()
  supply_cell_portal_type = "Sale Supply Cell"
  supply_line_id = "default_ssl"
  use_list = portal.portal_preferences.getPreferredSaleUseList()
  check_stock_availability = True
elif line_portal_type in portal.getPortalPurchaseTypeList():
  section_uid = delivery.getDestinationSectionUid()
  supply_cell_portal_type = "Purchase Supply Cell"
  supply_line_id = "default_psl"
  use_list = portal.portal_preferences.getPreferredPurchaseUseList()
elif line_portal_type in portal.getPortalInternalTypeList():
  section_uid = None
  supply_line_id = "default_isl"
  supply_cell_portal_type = "Internal Supply Cell"
  use_list = portal.portal_preferences.getPreferredPurchaseUseList() \
             + portal.portal_preferences.getPreferredSaleUseList()
elif line_portal_type in portal.getPortalInventoryMovementTypeList():
  section_uid = None
  no_inventory = True
  use_list = portal.portal_preferences.getPreferredPurchaseUseList() \
             + portal.portal_preferences.getPreferredSaleUseList()
else:
  message = 'Type of document not known to supply cell type.'
  return context.Base_redirect('view', keep_items=dict(
                          portal_status_message=Base_translateString(message)))

request= context.REQUEST

total_price = 0.0
status_message_dict = {}

for line in listbox:
  if 'listbox_key' in line and (line['title'] not in ('', None)
                                      or line['reference'] not in ('', None)
                                      or line.get('resource_relative_url', None) not in ('', None)):
    line_id = line['listbox_key']
    product = None

    # Copy user input
    request.form["field_listbox_reference_new_%s"%line_id] = line["reference"]
    request.form["field_listbox_title_new_%s"%line_id] = line["title"]

    # Retrieve the resource
    resource_relative_url = line.get('resource_relative_url')
    if resource_relative_url:
      product = portal.restrictedTraverse(resource_relative_url)
    else:
      use_uid_list = [portal.portal_categories.resolveCategory(use).getUid()
                                              for use in use_list]
      product_list = portal.portal_catalog(
                                portal_type=portal.getPortalResourceTypeList(),
                                title=line['title'],
                                default_use_uid=use_uid_list,
                                reference=line['reference'])
      if len(product_list) != 1:
        continue
      else:
        product = product_list[0].getObject()

    # Resource part
    line["resource_relative_url"] = product.getRelativeUrl() #cell.getResource()
    request.set("field_listbox_resource_relative_url_new_%s"%line_id,product.getRelativeUrl())

    request.form["field_listbox_quantity_unit_new_%s"%line_id] = product.getQuantityUnit()
    variation_list = line['variation_category_list']

    # Part for fast input wich checks inventory value
    if no_inventory is False:
      # First defined the price
      line["total_price"] = 0.0
      quantity = line.get('quantity')
      if quantity in (None, ""):
        line["quantity"] = 0.0
      if line['price'] in (None,""):
        if variation_list:
          # Retrieve the price from the cell
          # if we have variation defined
          try:
            supply_cell_list = product[supply_line_id].contentValues(portal_type=supply_cell_portal_type)
          except KeyError:
            # No price defined
            supply_cell_list = []
          for supply_cell in supply_cell_list:
            if supply_cell.getVariationCategoryList() == variation_list:
              line['price'] = supply_cell.getBasePrice() or 0
              line["total_price"] = line['quantity'] * line['price']
              break
        else:
          # Retrieve the price from the line
          # if we have no variation defined
          try:
            supply_line = product[supply_line_id]
            line['price'] = supply_line.getBasePrice() or 0
            line["total_price"] = line['quantity'] * line['price']
          except KeyError:
            # No price defined
            pass
      else:
        # Use the price defined by the user
        line["total_price"] = line['quantity'] * line['price']

      request.form["field_listbox_price_new_%s"%line_id] = line['price']
      request.form["field_listbox_total_price_new_%s"%line_id] = line['total_price']
      # Update total price of fast input
      total_price +=line['total_price']

      # Part for products
      if product.getPortalType() in portal.getPortalProductTypeList():
        # Inventory part
        if variation_list:
          available_inv = request.form["field_listbox_available_quantity_new_%s"%line_id] = product.getAvailableInventory(
                                           section_uid=section_uid,
                                           variation_text=variation_list)
          request.form['field_listbox_inventory_new_%s'%line_id] = product.getInventory(
                                           section_uid=section_uid,
                                           variation_text=variation_list)
          request.form["field_listbox_current_quantity_new_%s"%line_id] = product.getCurrentInventory(
                                           section_uid=section_uid,
                                           variation_text=variation_list)
        else:
          available_inv = request.form["field_listbox_available_quantity_new_%s"%line_id] = product.getAvailableInventory(section_uid=section_uid)
          request.form['field_listbox_inventory_new_%s'%line_id] = product.getInventory(section_uid=section_uid)
          request.form["field_listbox_current_quantity_new_%s"%line_id] = product.getCurrentInventory(section_uid=section_uid)

        # Check if quantity is available
        if check_stock_availability and available_inv < line["quantity"]:
          status_message_dict.setdefault(product.getRelativeUrl(), []).append(line['listbox_key'])

status_message_list = []
portal_status_message = None
if status_message_dict:
  for product_relative_url, line_id_list in status_message_dict.items():
    product = portal.restrictedTraverse(product_relative_url)
    mapping = {'product_title': product.getTitle(''),
               'product_reference': product.getReference('')}
    if len(line_id_list) > 1:
      line_id_list.sort()
      message = 'Asked quantity of "${product_title} - ${product_reference}" is not available in inventory for lines ${line_id}'
      mapping['line_id'] = ', '.join(line_id_list)
    else:
      message = 'Asked quantity of "${product_title} - ${product_reference}" is not available in inventory for line ${line_id}'
      mapping['line_id'] = line_id_list[0]
    status_message_list.append(Base_translateString(message, mapping=mapping))
  portal_status_message = ' -- '.join(status_message_list)

request.form["field_my_total_price"] = total_price

context.Base_updateDialogForm(listbox=listbox,update=1,kw=kw)
return context.Base_renderForm(
  request.form['dialog_id'],
  message=portal_status_message
)
