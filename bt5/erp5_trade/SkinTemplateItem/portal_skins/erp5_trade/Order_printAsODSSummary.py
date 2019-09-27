# We wants to get data in order to do a nice summary of items inside the order
# This report will mainly usefull when the same resource is ordered on many
# different lines
from Products.ERP5Type.Log import log
if target_language:
  container.REQUEST['AcceptLanguage'].set(target_language, 10)

unit_title_dict = {}
total_quantity_dict = {}
unit_price_dict = {}
total_price_dict = {}
error = None
error_kw = {}
default_quantity_unit = None
default_quantity_unit_title = ''
resource_dict = {}
summary_quantity_dict = {}
object_list = []
untranslatable_column_list = [] # We should not translate some columns
full_total_price = 0
worker_column_list = []
source_trade_dict = {}

context_relative_url = context.getRelativeUrl()

def sortMovement(a, b):
  return cmp(a.getRelativeUrl(), b.getRelativeUrl())

movement_type_list = context.getPortalMovementTypeList()
line_list = [x for x in context.getIndexableChildValueList() if x.getPortalType() in \
              movement_type_list]
line_list.sort(sortMovement)

order_type_list = context.getPortalOrderTypeList()
def getMovementTitle(movement):
  title = movement.getTitle()
  parent_value = movement.getParentValue()
  while parent_value.getPortalType() not in order_type_list:
    title = parent_value.getTitle() + ' / ' + title
    log('parent_value', parent_value)
    parent_value = parent_value.getParentValue()
  return title

if len(quantity_unit_list) != 1:
  error = "You should select only one quantity unit"
else:
  default_quantity_unit = quantity_unit_list[0]
  default_quantity_unit_title = context.portal_categories.\
      restrictedTraverse('quantity_unit/' + default_quantity_unit).getTitle()

column_list = [('reference', 'Reference'), ('title', 'Title'), \
    ('description', 'Description'), ('start_date', 'Shipping Date'), \
    ('stop_date', 'Delivery Date'), ('per_line_total_price', 'Total Price')]
if error is None:
  for line in line_list:
    if error is not None:
      break
    resource = line.getResource()
    line_kw = {}
    # for the per line total price
    total_price = line.getTotalPrice()
    line_kw['per_line_total_price'] = line.getTotalPrice()
    if len(line) != 0:
      line_kw['stop_date'] = ""
    else:
      if resource is not None:
        if not resource in resource_dict:
          resource_value = line.getResourceValue()
          resource_dict[resource] = resource_value
          current_column = (resource, resource_value.getTitle())
          column_list.append(current_column)
          untranslatable_column_list.append(current_column)
          unit_price_dict[resource] = line.getPrice()
          unit_title_dict[resource] = line.getQuantityUnitTitle()
        quantity_unit = line.getQuantityUnit()
        if line.getPrice() != unit_price_dict[resource]:
          error = "Same resource has several prices, "\
              + "not handled by this report yet, check: ${line_title}"
          error_kw['line_title'] = getMovementTitle(line)
          continue
        if line.getQuantityUnitTitle() != unit_title_dict[resource]:
          error = "Same resource has several units, " \
              + "not handled by this report yet, check: ${line_title}"
          error_kw['line_title'] = getMovementTitle(line)
          continue
        source_trade_list = line.getSourceTradeList()
        if len(source_trade_list) != 1:
          error = "This report assume one Supplier or Worker for each line, " \
              + "check: ${line_title}"
          error_kw['line_title'] = getMovementTitle(line)
          continue
        source_trade = source_trade_list[0]
        if source_trade not in source_trade_dict:
          source_trade_value = line.getSourceTradeValue()
          source_trade_dict[source_trade] = source_trade_value
          current_column = (source_trade, source_trade_value.getTitle())
          worker_column_list.append(current_column)
          untranslatable_column_list.append(current_column)
        # For the line displaying total quantity 
        quantity = line.getQuantity()
        total_quantity_dict[resource] = total_quantity_dict.get(resource, 0) + quantity
        if quantity_unit == default_quantity_unit:
          total_quantity_dict[source_trade] = total_quantity_dict.get(source_trade, 0) + quantity
        # For the line displaying total price 
        total_price_dict[resource] = total_price_dict.get(resource, 0) + total_price
        if quantity_unit == default_quantity_unit:
          total_price_dict[source_trade] = total_price_dict.get(source_trade, 0) + total_price
        full_total_price += total_price
        # For the display of the quantity for resource and source_trade
        line_kw[resource] = quantity
        if quantity_unit == default_quantity_unit:
          line_kw[source_trade] = quantity
          # Add the column wich is a summary between column of resources and column 
          # of source_trades
          line_kw['summary_quantity'] = quantity
    line = line.asContext(**line_kw)
    object_list.append(line)


if error is not None:
  previous_skin_selection = container.REQUEST.get('previous_skin_selection', None)
  context.getPortalObject().changeSkin(previous_skin_selection)
  return context.Base_redirect('view', keep_items={'portal_status_message': context.Base_translateString(error, mapping=error_kw)})

# Add a line for unit titles
for source_trade in source_trade_dict:
  unit_title_dict[source_trade] = default_quantity_unit_title
unit_title_dict['summary_quantity'] = default_quantity_unit_title
unit_title_object = context.asContext(title = "Unit",
                                      reference = "",
                                      stop_date = "",
                                          **unit_title_dict)
# Add a line for the number of unit per resource
# First compute the summary quantity
for source_trade in source_trade_dict:
  total_quantity_dict['summary_quantity'] = total_quantity_dict.get('summary_quantity', 0) + \
             total_quantity_dict.get(source_trade, 0)
total_quantity_object = context.asContext(title = "Total Quantity",
                                          reference = "",
                                          stop_date = "",
                                      **total_quantity_dict)
# Add a line for the object unit price
# and Compute the unit price for each source_trade
for source_trade in source_trade_dict:
  if total_price_dict.get(source_trade, 0) != 0 and \
      total_quantity_dict.get(source_trade, 0) != 0:
    unit_price_dict[source_trade] = \
      total_price_dict.get(source_trade, 0) / total_quantity_dict.get(source_trade, 0)
unit_price_object = context.asContext(title = "Unit Price",
                                      reference = "",
                                      stop_date = "",
                                      **unit_price_dict)
# Add a line for the total price per resource
for source_trade in source_trade_dict:
  total_price_dict['summary_quantity'] = \
    total_price_dict.get('summary_quantity', 0) + total_price_dict.get(source_trade, 0)
total_price_dict['per_line_total_price'] = full_total_price
total_price_object = context.asContext(title = "Total Price",
                                       reference = "",
                                       stop_date = "",
                                      **total_price_dict)
object_list = [unit_title_object, total_quantity_object, unit_price_object,
               total_price_object] + object_list
column_list.extend([('summary_quantity', 'Total Service')])
column_list.extend(worker_column_list)


context = context.asContext(
                 object_list = object_list,
                 untranslatable_column_list = untranslatable_column_list,
                 column_list = column_list)

return context.Order_viewODSSummary(format=format)
