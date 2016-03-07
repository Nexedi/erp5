project_module = context.getPortalObject().project_module
for month in (1, 2, 3):
  try:
    project_module.manage_delObjects(ids=['test_project_%s' % month])
  except:
    pass
return "Deleted Successfully."
