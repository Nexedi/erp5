## Script (Python) "Delivery_rescueOrphanedMovement"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=fix=0
##title=
##
# Example code:

order_uid_list = context.getCausalityUidList()  # XXX We may need to filter portal_type

# Check each existing movement in delivery
attached_to_movement = []
for m in context.getMovementList():
  # simulation_movement = m.getDeliveryRelatedValueList()
  # Is there any orphaned movement
  result = context.Delivery_zGetOrphanedMovementList(order_uid_list = order_uid_list,
                                                  resource_uid = m.getResourceUid(),
                                                  variation_text = m.getVariationText())
  if len(result) > 0:
    for orphaned in result:
      print "Found orphaned movement %s attached to %s" % (orphaned.relative_url, m.getRelativeUrl())
      attached_to_movement.append(orphaned.relative_url)
      if fix:
        simulation_movement = orphaned.getObject()
        quantity = simulation_movement.getQuantity()
        simulation_movement.setDeliveryValue(m)
        m.setQuantity(quantity)
        print "  Fixed orphaned movement %s attached to %s with quantity %s" % (orphaned.relative_url, m.getRelativeUrl(), quantity)

# Check each orphaned movement
result = context.Delivery_zGetOrphanedMovementList(  order_uid_list = order_uid_list )
for orphaned in result:
  if orphaned.relative_url not in attached_to_movement:
    print "Found orphaned movement %s which required new line/cell" % orphaned.relative_url

return printed
