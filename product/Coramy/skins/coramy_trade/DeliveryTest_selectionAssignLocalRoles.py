## Script (Python) "DeliveryTest_selectionAssignLocalRoles"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
selection = context.portal_selections.getSelectionFor('purchase_packing_list_selection',REQUEST=context.REQUEST)
delivery_list = selection(context=context)
request = context.REQUEST

for delivery_item in delivery_list:
  delivery = delivery_item.getObject()

  if delivery is not None :
    order_list = delivery.getCausalityValueList()
    if len(order_list) > 0 :
      order = order_list[0]
      # what's the gestionaire of this order
      user_name = ''
      # are we on a sales order or puchase order ?
      if order.getPortalType() == 'Purchase Order' :
        user_name = order.getDestinationAdministrationPersonTitle().replace(' ','_')
        delivery.assign_gestionaire_designe_roles(user_name = user_name)

return 'fait'
