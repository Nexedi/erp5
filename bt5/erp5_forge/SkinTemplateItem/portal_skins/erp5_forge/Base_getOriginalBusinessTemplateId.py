installed_bts = context.getPortalObject()['portal_templates'].getInstalledBusinessTemplatesList()
for bt in installed_bts:
  if file in bt.getItemsList():
    return bt.getId()

built_bts = context.getPortalObject()['portal_templates'].getBuiltBusinessTemplatesList()
for bt in built_bts:
  if file in bt.getItemsList():
    return bt.getId()

return None
