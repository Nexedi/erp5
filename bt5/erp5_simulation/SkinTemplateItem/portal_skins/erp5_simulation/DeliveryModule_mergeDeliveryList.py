REQUEST=context.REQUEST
selection_name = REQUEST['selection_name']
object_list = context.portal_selections.getSelectionValueList(selection_name, context=context, REQUEST=REQUEST)
delivery_list = []
for o in object_list:
  delivery_list.append(o)

Base_translateString = context.Base_translateString

if len(delivery_list) < 2:
  message =  Base_translateString('Please select more than one items.')
else:
  error_list = context.portal_simulation.mergeDeliveryList(delivery_list)
  if not error_list:
    message = Base_translateString('Merged.')
  else:
    message = ' '.join([str(x) for x in error_list])

return context.Base_redirect('view',keep_items={'portal_status_message': message})
