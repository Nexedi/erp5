test_result = sci['object']
kw = sci['kwargs']
test_result.setStopDate(kw.get('date') or DateTime())

def unexpected(test_result):
  # We must change to only distinguish SKIP/EXPECTED/UNEXPECTED, instead of
  # SKIP/FAIL/ERROR. NEO reports EXPECTED as FAIL and we want to mark it as
  # passed if there's no unexpected failures.
  return test_result.getSourceProjectTitle() != "NEO R&D"

def shouldRetry(test_result):
  """Should the test result be retried ?

  We retry test result line once or twice for known really flaky tests,
  Unless if there's already another failed test result line, in that
  Case we don't retry.
  """
  if 'ERP5.UnitTest-TestRunner' in test_result.getParentValue().getTitle():
    retry_count = test_result.getProperty('test_result_retry_count') or 0
    max_allowed_retry_count = 1
    # retry more some tests failing a lot
    if test_result.getTitle() in (
      'erp5_officejs_ui_test:testFunctionalOfficeJSoOoSpreadsheet',
      'erp5_advanced_ecommerce_test:testFunctionalAdvancedECommerce',
    ):
      max_allowed_retry_count = 2
    if retry_count < max_allowed_retry_count:
      another_test_failed = False
      for other_test_result_line in test_result.getParentValue().contentValues(portal_type='Test Result Line'):
        if test_result != other_test_result_line and other_test_result_line.getStringIndex() in ('UNKNOWN', 'FAILED'):
          another_test_failed = True
      return not another_test_failed

  return False


if test_result.getPortalType() == 'Test Result':
  has_unknown_result = False
  edit_kw = dict(duration=0,
                 all_tests=0,
                 errors=0,
                 failures=0,
                 skips=0)
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
  if all_tests is None:
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
                   html_test_result=html_test_result)
  if status == 'FAILED' and shouldRetry(test_result):
    test_result.edit(
        test_result_retry_count=1 + (test_result.getProperty('test_result_retry_count') or 0),
        string_index='RETRYING',
    )
    test_result.redraft(comment="Retried after a first failure")
else:
  raise NotImplementedError("unknown type : %r" % test_result.getPortalType())
