test_result = sci['object']
kw = sci['kwargs']
test_result.setStopDate(kw.get('date') or DateTime())
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
    has_unknown_result = has_unknown_result or line.getStringIndex() == 'UNKNOWN'
  if has_unknown_result or edit_kw['errors'] or edit_kw['failures']:
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
  elif errors or failures:
    status = 'FAILED'
  else:
    status = 'PASSED'
  duration = kw.get('duration')
  if duration is None:
    duration = (test_result.getStopDate() - test_result.getStartDate()) * (24*60*60)
  cmdline = kw.get('command', getattr(test_result, 'cmdline', ''))
  if same_type(cmdline, []):
    cmdline = ' '.join(map(repr, cmdline))
  stdout = kw.get('stdout', getattr(test_result, 'stdout', ''))
  stderr = kw.get('stderr', getattr(test_result, 'stderr', ''))
  html_test_result = kw.get('html_test_result', getattr(test_result, 'html_test_result', ''))
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
else:
  raise NotImplementedError("unknown type : %r" % test_result.getPortalType())
