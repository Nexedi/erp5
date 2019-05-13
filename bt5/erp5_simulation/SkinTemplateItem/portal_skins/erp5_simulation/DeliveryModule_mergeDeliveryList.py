REQUEST=context.REQUEST
selection_name = REQUEST['selection_name']
object_list = context.portal_selections.getSelectionValueList(selection_name, context=context, REQUEST=REQUEST)
delivery_list = []
for o in object_list:
  delivery_list.append(o)

if len(delivery_list) < 2:
  ret_url = context.absolute_url() + '/' + form_id
  qs = '?portal_status_message=Please+select+more+than+one+items.'
else:
  ret_url = context.absolute_url() + '/' + form_id
  error_list = context.portal_simulation.mergeDeliveryList(delivery_list)
  if not error_list:
    qs = '?portal_status_message=Merged.'
  else:
    qs = '?portal_status_message=%s' % (' '.join(error_list))

return REQUEST.RESPONSE.redirect( ret_url + qs )
