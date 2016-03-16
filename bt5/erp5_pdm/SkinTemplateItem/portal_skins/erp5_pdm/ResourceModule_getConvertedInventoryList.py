kw['resource_uid'] = context.ResourceModule_getSelection().getUidList()

if kw.setdefault('inventory_list', 1):
  kw.update(group_by_node = 1, group_by_resource = 0)
else:
  kw.update(ignore_group_by = 1)

return context.getPortalObject().portal_simulation \
              .getConvertedInventoryList(simulation_period='All', **kw)
