from DateTime import DateTime
form = context.REQUEST.form

# find project by title
test_suite = form.get('test_suite', None)
project = context.ERP5Site_getProjectFromTestSuite(test_suite)

# create test result object
# test_report = context.newContent( # Dangerous
test_report = context.getPortalObject().test_result_module.newContent(
  id=form.get('test_report_id'),
  portal_type='Test Result',
  title=test_suite,
  string_index=form.get('result'),
  source_project_value=project)

# update security
test_report.updateLocalRolesOnSecurityGroups()

test_report.start(date=DateTime(form.get('launch_date')))
