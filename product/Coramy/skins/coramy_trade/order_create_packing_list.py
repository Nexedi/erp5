## Script (Python) "order_create_packing_list"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
movement_list = []
order = context

if order.getPortalType() == 'Purchase Order' :
  filter_dict = {'portal_type': 'Purchase Order Line'}
else :
  filter_dict = {'portal_type': 'Sales Order Line'}

movement_list += order.getOrderRelatedValueList(portal_type = 'Simulation Movement')
for order_line in order.contentValues(filter=filter_dict) :
  movement_list += order_line.getOrderRelatedValueList(portal_type = 'Simulation Movement')
  for cell in order_line.contentValues(filter={'portal_type': 'Delivery Cell'}) :
     movement_list += cell.getOrderRelatedValueList(portal_type = 'Simulation Movement')

root_group = context.portal_simulation.collectMovement(movement_list)
delivery_list = context.portal_simulation.buildDeliveryList(root_group)

# what's the gestionaire of this order
user_name = ''
# are we on a sales order or puchase order ?
if order.getPortalType() == 'Sales Order' :
  user_name = order.getSourceAdministrationTitle().replace(' ','_')
elif order.getPortalType() == 'Purchase Order' :
  user_name = order.getDestinationAdministrationPersonTitle().replace(' ','_')

for delivery in delivery_list :
  # update the state of the created deliveries to 'confirmed'
  delivery.confirm()
  # update local_roles
  delivery.assign_gestionaire_designe_roles(user_name = user_name)

return delivery_list
