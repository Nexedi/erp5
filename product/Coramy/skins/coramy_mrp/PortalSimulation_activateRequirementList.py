# Erase existing auto_planned
order_list = context.portal_catalog(simulation_state="auto_planned", parent_uid=[context.ordre_fabrication.getUid()])
order_id_list = map(lambda x:x.id,order_list)
object_id_list = context.ordre_fabrication.objectIds()
order_id_list = filter(lambda x: x in object_id_list, order_id_list)
context.ordre_fabrication.deleteContent(order_id_list)

order_list = context.portal_catalog(simulation_state="auto_planned", parent_uid=[context.commande_achat.getUid()])
order_id_list = map(lambda x:x.id,order_list)
object_id_list = context.commande_achat.objectIds()
order_id_list = filter(lambda x: x in object_id_list, order_id_list)
context.commande_achat.deleteContent(order_id_list)

# Stock sourcing states
#source_state_list = ('auto_planned', 'planned', 'ordered', 'confirmed', 'getting_ready', 'ready', 'delivered', 'started', 'stopped', 'invoiced')
source_state_list = None

# Get inventory list
inventory_list = context.SimulationTool_getGroupFutureInventoryList(simulation_state=source_state_list)
# Commit SQL
# context.portal_simulation.commitTransaction()

# Call PortalSimulation_buildRequirementOrder for each missing resource
for inventory_item in inventory_list:
  if inventory_item.inventory < 0 and inventory_item.inventory is not None:
    # We should use a queue here rather than a dict - OVERKILL
    movement = inventory_item.getObject()
    if movement is not None:
      resource = movement.getResourceValue()
      if resource is not None:
        # Only source negative stock
        print "Activate Build Order for %s for missing quantity %s" % (inventory_item.resource_relative_url, inventory_item.inventory)
        resource.activate(priority=2).PortalSimulation_buildRequirementOrder(resource=inventory_item.resource_relative_url)

return printed

