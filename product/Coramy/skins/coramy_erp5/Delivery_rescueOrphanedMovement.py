## Script (Python) "Delivery_rescueOrphanedMovement"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=fix=0
##title=Tries to find orphaned movements to fix a given delivery
##
# Example code:

order_uid_list = list(context.getCausalityUidList()) + [context.getUid()]  # XXX We may need to filter portal_type
#order_uid_list = context.getCausalityUidList()
# We must consider delivery rules and deliveries without order (ie. order is delivery)

# Check each existing movement in delivery
attached_to_movement = []
requires_delivery_rule = []
requires_new_delivery = []
for m in context.getMovementList():
  simulation_movement_list = m.getDeliveryRelatedValueList()
  if len(simulation_movement_list) > 0:
    # This movement is simulated
    # let us check if simulation movements point where they should
    for orphaned in simulation_movement_list:
      simulation_movement = orphaned.getObject()
      if simulation_movement.getDelivery() != m.getRelativeUrl():
        print "Found inconsistent simulation movement %s attached to %s instead of %s" % (simulation_movement.getRelativeUrl(), simulation_movement.getDelivery(), m.getRelativeUrl())
        print "##Reindexing"        
        simulation_movement.immediateReindexObject() # Always fix
  else:
    # This movement is not simulated
    # find potential orphaned
    result = context.Delivery_zGetOrphanedMovementList(order_uid_list = order_uid_list,
                                                    resource_uid = m.getResourceUid(),
                                                    variation_text = m.getVariationText())
    if len(result) > 0:
      for orphaned in result:
        simulation_movement = orphaned.getObject()
        initial_quantity = m.getQuantity()
        quantity = simulation_movement.getQuantity()
        print "Found orphaned movement %s attached to %s. (%s in simulation instead of %s in delivery)" % (orphaned.relative_url, m.getRelativeUrl(), quantity, initial_quantity)
        attached_to_movement.append(orphaned.relative_url)
        if fix:
          # More job is required here XXX
          simulation_movement.setDeliveryValue(m)
          m.setQuantity(quantity)
          print "  Fixed orphaned movement %s attached to %s with simulation quantity %s" % (orphaned.relative_url, m.getRelativeUrl(), quantity)
    else:
      requires_delivery_rule.append(m)

# Check each orphaned movement related to orders which we came from
print "##Building orphaned list"
result = context.Delivery_zGetOrphanedMovementList(  order_uid_list = order_uid_list )
#return map(lambda x:x.portal_type, result)
for orphaned in result:
  if orphaned.relative_url not in attached_to_movement:
    print "Found orphaned movement %s which requires new delivery" % orphaned.relative_url
    simulation_movement = orphaned.getObject()
    if simulation_movement is not None:
      try:
        simulation_movement.getDeliveryValue()
      except:
        return str(orphaned.portal_type)
      if simulation_movement.getDeliveryValue() is None:
        simulation_movement.setDelivery(None)
        requires_new_delivery.append(simulation_movement)
      else:
        print "Error: has previous delivery but found as orphaned movement (%s)" % orphaned.relative_url

# Build new deliveries
if fix:
  print "Building new packing lists"
  root_group = context.portal_simulation.collectMovement(requires_new_delivery)
  delivery_list = context.portal_simulation.buildDeliveryList(root_group)
  for delivery in delivery_list:
    print "  New delivery %s for causality %s" % (delivery.getRelativeUrl(), ' '.join(delivery.getCausalityList()))

return printed
