import json
from DateTime import DateTime

portal_catalog = context.getPortalObject().portal_catalog
test_result_kw = {'portal_type': 'Test Result',
                  'simulation_state': ('stopped', 'failed'),
                  'delivery.start_date': ">= " + (DateTime()-365).strftime("%Y/%m/%d"),
                 }

# one row per project, instead of one row per test result of the last 365 days
project_relative_url_list = [x.source_project__relative_url for x in portal_catalog(
  source_project__validation_state='validated',
  select_list=['source_project__relative_url'],
  group_by=['source_project__relative_url'],
  **test_result_kw)]

result_dict = {}
for project_relative_url in project_relative_url_list:
  for test_result in portal_catalog(
      source_project__relative_url=project_relative_url,
      sort_on=[('modification_date', 'descending')],
      limit=1,
      **test_result_kw):
    result_dict[project_relative_url] = {'all_tests': test_result.all_tests,
                                         'failures': test_result.failures}
return json.dumps(result_dict, indent=2)
