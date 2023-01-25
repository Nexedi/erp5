form = context.REQUEST.form
test_result_file = form.get('filepath')
test_report_id = form.get('test_report_id', '')

# find already created test result object
test_report = getattr(context, test_report_id)

# parse test log file to get number of tests (successfull/failed)
all_test_results = context.parseTestSuiteResults(test_result_file)

all_tests = 0
errors = 0
failures = 0
skips = 0

# 'edit' magic key is used to pass edit parameter from the external method to this script
# this is horrible XXX
edit_dict = all_test_results.pop('edit', None)
if edit_dict:
  test_report.edit(**edit_dict)

for test_id, test_result in all_test_results.items():
  # save log files
  log_files = test_result['files']

  all_tests += test_result['all_tests']
  errors += test_result['errors']
  failures += test_result['failures']
  skips += test_result['skips']

  # save passed initial test state
  test_report.newContent(
            portal_type='Test Result Line',
            id=test_id,
            title=test_result.get('test_case'),
            string_index=test_result.get('result'),
            all_tests=test_result.get('all_tests'),
            html_test_result=test_result.get('html_test_result'),
            errors=test_result.get('errors'),
            failures=test_result.get('failures'),
            skips=test_result.get('skips'),
            duration=test_result.get('seconds'),
            cmdline=log_files.get('cmdline'),
            stdout=log_files.get('stdout'),
            stderr=log_files.get('stderr'),)


test_report.edit(string_index=form.get('result'),
                 all_tests=all_tests,
                 errors=errors,
                 failures=failures,
                 skips=skips)

test_report.stop()
