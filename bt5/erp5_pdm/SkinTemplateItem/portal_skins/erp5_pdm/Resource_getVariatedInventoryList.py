kwargs = {}
kwargs.update(
          resource_uid = context.getUid(),
          group_by_node = 0,
          group_by_resource = 0,
          group_by_variation = 1,
          node_uid = context.restrictedTraverse(kw['node']).getUid(),
          at_date = kw.get('at_date'),
)

return context.getPortalObject().portal_simulation.getAllInventoryList(**kwargs)
