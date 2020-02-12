import json
from DateTime import DateTime

result_dict = {}
catalog_kw = {'portal_type' : 'Test Result',
              'simulation_state': ('stopped', 'failed'),
              'source_project__validation_state': 'validated',
              'delivery.start_date': ">= " + (DateTime()-365).strftime("%Y/%m/%d"),
             }
sort_on = [('modification_date', 'descending')]
select_list = ['source_project__relative_url']

for test_result in context.portal_catalog(sort_on=sort_on, select_list=select_list, **catalog_kw):
  # get the first test result (most recent) for each project
  if not test_result.source_project__relative_url in result_dict:
    result_dict[test_result.source_project__relative_url] = {'all_tests': test_result.all_tests,
                                                             'failures': test_result.failures}
return json.dumps(result_dict, indent=2)
