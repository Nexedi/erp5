## Script (Python) "Delivery_mergeDeliveryList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id=''
##title=Merge deliveries into one
##
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
  qs = '?portal_status_message=Merged.'
  context.portal_simulation.mergeDeliveryList(delivery_list)

return REQUEST.RESPONSE.redirect( ret_url + qs )
