if context.isResourceType():
  uid_list = context.getUid()
else:
  uid_list = context.ResourceModule_getSelection().getUidList()

return context.portal_simulation.getInventoryList(transformed_resource=transformed_resource_list,resource_uid=uid_list)
