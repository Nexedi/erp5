import re
test_result = sci['object']
kw = sci['kwargs']
test_result.setStopDate(kw.get('date') or DateTime())

def unexpected(test_result):
  # We must change to only distinguish SKIP/EXPECTED/UNEXPECTED, instead of
  # SKIP/FAIL/ERROR. NEO reports EXPECTED as FAIL and we want to mark it as
  # passed if there's no unexpected failures.
  return test_result.getSourceProjectTitle() != "NEO R&D"


def shouldRetry(test_result_line):
  # type: (erp5.portal_type.TestResultLine,) -> bool
  """Should the test result line be retried ?

  We retry test result line once for tests matching pattern defined on test suite.
  Unless if there's already another failed test result line, in that case we don't retry.
  """
  if test_result_line.getProperty('test_result_retry_count') or 0:
    return False

  test_result = test_result_line.getParentValue()
  for other_test_result_line in test_result.contentValues(portal_type='Test Result Line'):
    if test_result_line != other_test_result_line and other_test_result_line.getStringIndex() in ('UNKNOWN', 'FAILED'):
      return False

  test_suite_data = test_result.TestResult_getTestSuiteData()
  if not test_suite_data:
    return False
  if not test_suite_data['retry_test_pattern']:
    return False
  return re.search(test_suite_data['retry_test_pattern'], test_result_line.getTitle() or '')


if test_result.getPortalType() == 'Test Result':
  has_unknown_result = False
  edit_kw = dict(duration=0,
                 all_tests=0,
                 errors=0,
                 failures=0,
                 skips=0,
                 test_result_retry_count=0)
  for line in test_result.objectValues(portal_type='Test Result Line'):
    for prop in edit_kw:
      try:
        edit_kw[prop] = edit_kw[prop] + line.getProperty(prop, 0)
      except TypeError as e:
        context.log("", repr(e))
        has_unknown_result = True
      else:
        if line.getStringIndex() == 'UNKNOWN':
          has_unknown_result = True
  if has_unknown_result or edit_kw['errors'] or (
      edit_kw['failures'] and unexpected(test_result)):
    status = 'FAIL'
  else:
    status = 'PASS'
  test_result.edit(string_index=status, **edit_kw)
  test_result.activate().TestResult_afterComplete()
elif test_result.getPortalType() == 'Test Result Line':
  all_tests = kw.get('test_count')
  errors = kw.get('error_count', 0)
  failures = kw.get('failure_count', 0)
  skips = kw.get('skip_count', 0)
  if (all_tests is None) or (all_tests == 0):
    status = 'UNKNOWN'
    all_tests = 0
  elif errors or failures and unexpected(test_result.getParentValue()):
    status = 'FAILED'
  else:
    status = 'PASSED'
  duration = kw.get('duration')
  if duration is None:
    duration = (test_result.getStopDate() - test_result.getStartDate()) * (24*60*60)
  cmdline = kw.get('command', '')
  if same_type(cmdline, []):
    cmdline = ' '.join(map(repr, cmdline))
  stdout = kw.get('stdout', '')
  stderr = kw.get('stderr', '')
  html_test_result = kw.get('html_test_result', '')
  test_result.edit(cmdline=cmdline,
                   stdout=stdout,
                   stderr=stderr,
                   string_index=status,
                   duration=duration,
                   all_tests=all_tests,
                   errors=errors,
                   failures=failures,
                   skips=skips,
                   test_result_retry_count=(test_result.getProperty('test_result_retry_count') or 0),
                   html_test_result=html_test_result)
  if status == 'FAILED' and shouldRetry(test_result):
    test_result.edit(
        test_result_retry_count=test_result.getProperty('test_result_retry_count') + 1,
        string_index='RETRYING',
    )
    test_result.redraft(comment="Retried after a first failure")
else:
  raise NotImplementedError("unknown type : %r" % test_result.getPortalType())
