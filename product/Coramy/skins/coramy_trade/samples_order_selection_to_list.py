## Script (Python) "samples_order_selection_to_list"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
selection = context.portal_selections.getSelectionFor('order_selection',REQUEST=context.REQUEST)
order_sql_list = selection(context=context)
request = context.REQUEST
order_id_list =[]

for order_item in order_sql_list :
  order=order_item.getObject()
  if order <> None :
    order_id_list.append(order.getId())

return order_id_list
