## Script (Python) "ProductionOrder_buildDeliveryList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Build Deliveries for a Production Order
##
order = context

# Get movement list for production
movement_list = context.ProductionOrder_getMaterialProductionMovementList()
root_group = context.portal_simulation.collectMovement(movement_list)
delivery_list = context.portal_simulation.buildDeliveryList(root_group)

# Get movements for sourcing
movement_list = context.ProductionOrder_getMaterialSourcingMovementList()
root_group = context.portal_simulation.collectMovement(movement_list)
delivery_list += context.portal_simulation.buildDeliveryList(root_group)

# Get movements for outcome
movement_list = context.getOrderRelatedMovementList()
root_group = context.portal_simulation.collectMovement(movement_list)
delivery_list += context.portal_simulation.buildDeliveryList(root_group)

# what's the gestionaire of this order
user_name = ''
# are we on a production order ?
if order.getPortalType() == 'Production Order' :
  try :
    user_name = order.getDestinationAdministrationPersonTitle().replace(' ','_')
  except :
    user_name = ''

for delivery in delivery_list :
  # update the state of the created deliveries to 'confirmed'
  delivery.confirm()
  # update local_roles
  delivery.assign_gestionaire_designe_roles(user_name = user_name)

return map(lambda o:o.getRelativeUrl(), delivery_list)
