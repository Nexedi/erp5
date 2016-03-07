project_module = context.getPortalObject().project_module
for month in (1, 2, 3):
  project_module.newContent(portal_type='Project',
                            id='test_project_%s' % month,
                            title='test_project_%s' % month,
                            start_date=DateTime(2010, month, 1))
return "Projects Created."
