"""List Method script to show only inventory for destination"""

# When the delivery does not have a resource, returns empty list.
# Otherwise it returns all the inventories in your ERP5 site.
production_delivery = context
movement_list = production_delivery.getMovementList()
empty = True
for movement in movement_list:
  if movement.getResource() not in (None, ''):
    empty = False
    break
if empty:
  return []

portal_type_dict_mapping = {
  'Production Order' : {'node_uid' : context.getDestinationUid()},
}
kw = {}
kw['group_by_node'] = 1
kw['group_by_section'] = 0
kw['group_by_variation'] = 1

kw.update( **portal_type_dict_mapping.get(context.getPortalType(),{}) )
return context.getFutureInventoryList(*args,**kw)
