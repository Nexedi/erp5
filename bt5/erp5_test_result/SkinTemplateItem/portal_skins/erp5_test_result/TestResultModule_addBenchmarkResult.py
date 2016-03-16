project = context.ERP5Site_getProjectFromTestSuite(project_title)

# create test result object
benchmark_report = context.newContent(
  portal_type='Benchmark Result',
  title=title,
  source_project_value=project,
  command_line=command_line)

# update security
benchmark_report.updateLocalRolesOnSecurityGroups()

from DateTime import DateTime
benchmark_report.start(date=DateTime())

return benchmark_report
