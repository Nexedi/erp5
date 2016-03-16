# Look at all items availables for the source and then
# display them on a listbox so that the user will be able
# to select them
request = context.REQUEST
item_portal_type_list = ["Checkbook","Check"]
node = context.getBaobabSource()
destination_payment = request.get('destination_payment', None)

# retrieve listbox limit
nb_lines = int(kw.get('list_lines', 20))
limit_start = int(kw.get('list_start', 0))
limit = limit_start, nb_lines

simulation_state = None
model_filter_dict = {}
fast_input_type = getattr(request, 'your_fast_input_type', None)
if fast_input_type is None:
  fast_input_type = getattr(request, 'field_your_fast_input_type')

# retrieve reference field to filter list
reference = getattr(request, 'your_reference', None)
if reference is None:
  reference = getattr(request, 'field_your_reference', None)

# filter by checkbook model
checkbook_model = getattr(request, 'your_checkbook_model', None)
if checkbook_model is None:
  checkbook_model = getattr(request, 'field_your_checkbook_model', None)

# filter by title (check numbers)
title = getattr(request, 'your_title', None)
if title is None:
  title = getattr(request, 'field_your_title', None)

disable_node = 0
at_date = context.getStartDate()
if fast_input_type == 'traveler_check_purchase':
  model_filter_dict['fixed_price']=1
  item_portal_type_list = ('Check',)
  destination_payment = context.getDestinationPayment()
  disable_node = 1
if fast_input_type == 'checkbook_delivery':
  destination_payment = context.getDestinationPayment()
elif fast_input_type == 'traveler_check_sale':
  model_filter_dict['fixed_price']=1
  item_portal_type_list = ('Check',)
elif fast_input_type == 'checkbook_movement':
  # Nothing special here
  pass
elif fast_input_type == 'checkbook_vault_transfer':
  # Nothing special here
  pass
elif fast_input_type == 'checkbook_usual_cash_transfer':
  model_filter_dict['fixed_price']=1
  item_portal_type_list = ('Check',)

listbox = context.Delivery_getCheckbookList(
                    item_portal_type_list=item_portal_type_list,
                    destination_payment=destination_payment,
                    model_filter_dict=model_filter_dict,
                    simulation_state=simulation_state,
                    disable_node=disable_node,
                    at_date=at_date,
                    node=node,
                    reference=reference,
                    title=title,
                    checkbook_model=checkbook_model,
                    limit=limit)
context.Base_updateDialogForm(listbox=listbox)

return context.ListBox_initializeFastInput()
