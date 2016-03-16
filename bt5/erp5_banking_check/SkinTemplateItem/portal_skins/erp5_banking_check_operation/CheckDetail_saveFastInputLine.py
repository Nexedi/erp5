portal = context.getPortalObject()
N_ = portal.Base_translateString

request  = context.REQUEST
message = N_("No+Lines+Created.")
redirect_url = '%s/view?%s' % ( context.absolute_url()
                              , 'portal_status_message=%s' % message
                              )

# The fast input contain no line, just return.
if listbox is None:
  return request[ 'RESPONSE' ].redirect( redirect_url )

# get the list of movement we need to create
# First call the first scripts wich check many things
error_value = 0
field_error_dict = {}
if check:
  (error_value, field_error_dict) = context.CheckDelivery_generateCheckDetailInputDialog(
                                     listbox=listbox,batch_mode=1,**kw)

request = context.REQUEST
resource = request.get('resource',None)
previous_resource = request.get('previous_resource',None)
line_portal_type = "Checkbook Reception Line"

if (error_value or (previous_resource not in('',None) and previous_resource!=resource)):
  return context.CheckDelivery_generateCheckDetailInputDialog(
                                     listbox=listbox,batch_mode=0,**kw)

item_model = context.getPortalObject().restrictedTraverse(resource)

item_module_id = 'checkbook_module'
if item_model.getPortalType()=='Check':
  item_module_id = 'check_module'

create_line = 0
aggregate_data_list = []
context.log('CheckDetail_saveFastInputLine, listbox',listbox)
number_of_line_created = 0
for line in listbox:
  add_line = 0
  quantity = line['quantity']
  price = line.get('price',None)
  price_currency = line.get('price_currency',None)
  line_kw_dict = {}
  line_kw_dict['resource'] = resource
  line_kw_dict['quantity'] = quantity
  if price not in ('',None):
    add_line = 1
    line_kw_dict['price'] = price
  if price_currency not in ('',None):
    line_kw_dict['price_currency'] = price_currency
  destination_payment_relative_url = line.get('destination_payment_relative_url',None)
  if destination_payment_relative_url not in (None,''):
    add_line = 1
    line_kw_dict['destination_payment'] = destination_payment_relative_url
  destination_trade_relative_url = line.get('destination_trade_relative_url',None)
  if destination_trade_relative_url not in (None,''):
    line_kw_dict['destination_trade'] = destination_trade_relative_url
  reference_range_min = line.get('reference_range_min',None)
  if reference_range_min not in (None,''):
    line_kw_dict['reference_range_min'] = reference_range_min
    add_line = 1
  reference_range_max = line.get('reference_range_max',None)
  if reference_range_max not in (None,''):
    line_kw_dict['reference_range_max'] = reference_range_max
    add_line = 1
  check_amount_relative_url = line.get('check_amount',None)
  if check_amount_relative_url not in (None,''):
    if check_amount_relative_url.startswith('check_amount'):
      check_amount_relative_url = check_amount_relative_url[len('check_amount/'):]
    line_kw_dict['check_amount'] = check_amount_relative_url
  check_type_relative_url = line.get('check_type',None)
  if check_type_relative_url not in (None,''):
    if check_type_relative_url.startswith('check_type'):
      check_type_relative_url = check_type_relative_url[len('check_type/'):]
    line_kw_dict['check_type'] = check_type_relative_url
    check_type = context.getPortalObject().restrictedTraverse(check_type_relative_url)
    line_kw_dict['price'] = check_type.getPrice()
    line_kw_dict['price_currency'] = check_type.getParentValue().getPriceCurrency()
  if add_line:
    number_of_line_created += 1
    context.newContent(portal_type=line_portal_type,**line_kw_dict)

if number_of_line_created>0:
  message = N_("Lines+Created.")
  redirect_url = '%s/view?%s' % ( context.absolute_url()
                                , 'portal_status_message=%s' % message
                                )
request[ 'RESPONSE' ].redirect( redirect_url )
