## Script (Python) "PortalSimulation_fixDeliveryRule"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
delivery_id = {}
delivery_list = []

for m in context.objectValues():
  id = '_'.join(m.getId().split('_')[0:4])
  if m.getDelivery() is not None:
    delivery = m.getDeliveryValue()
    delivery_id[id] = m.getDelivery()    
  else:
    delivery_list.append(m)
  m.setOrder(delivery_id[id])
  print "%s %s %s" % (id, m.getRelativeUrl(), delivery_id[id])


# Build deliveries
movement_group = context.portal_simulation.collectMovement(delivery_list)
delivery_list = context.portal_simulation.buildDeliveryList(movement_group)

# Change workflow state
for new_delivery in delivery_list :
   # Copy local roles
   for k, v in delivery.get_local_roles():
     new_delivery.manage_addLocalRoles(k,v)
   # update the state of the created deliveries to 'confirmed'
   #new_delivery.confirm()
   print "Created delivery %s" % new_delivery.getId()

return printed
