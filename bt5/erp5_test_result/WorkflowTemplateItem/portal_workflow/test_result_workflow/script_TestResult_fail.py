test_result = sci['object']
kw = sci['kwargs']
stop_date = kw.get('date') or DateTime()
test_result.setStopDate(stop_date)
if test_result.getPortalType() == 'Test Result Node':
  cmdline = kw.get('command', getattr(test_result, 'cmdline', ''))
  edit_kw = {}
  if same_type(cmdline, []):
    cmdline = ' '.join(map(repr, cmdline))
  if cmdline:
    edit_kw['cmdline'] = cmdline
  for key in ('stdout', 'stderr'):
    key_value = kw.get(key, getattr(test_result, key, ''))
    if key_value:
      edit_kw[key] = key_value
  test_result.edit(**edit_kw)
else:
  container.script_TestResult_complete(sci)
