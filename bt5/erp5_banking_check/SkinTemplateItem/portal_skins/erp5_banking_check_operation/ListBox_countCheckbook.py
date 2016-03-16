# Look at all items availables for the source and then
# display them on a listbox so that the user will be able
# to select them
request = context.REQUEST
item_portal_type_list = ["Checkbook","Check"]
node = context.getBaobabSource()

fast_input_type = getattr(request, 'your_fast_input_type', None)
if fast_input_type is None:
  fast_input_type = getattr(request, 'field_your_fast_input_type')

disable_node = 0
at_date = context.getStartDate()

if fast_input_type == 'traveler_check_purchase':
  item_portal_type_list = ('Check',)
  disable_node = 1

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

nb = context.Delivery_getCheckbookList(
                    item_portal_type_list=item_portal_type_list,
                    disable_node=disable_node,
                    at_date=at_date,
                    node=node,
                    reference=reference,
                    title=title,
                    checkbook_model=checkbook_model,                    
                    count=True)

return [[nb,],]
