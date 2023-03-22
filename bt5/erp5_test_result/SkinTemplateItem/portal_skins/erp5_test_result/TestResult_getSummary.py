"""
  Return for buildbot test summary info.
  status, all tests, failures, errors
"""
seconds = 0.0
for obj in context.contentValues():
  seconds += obj.getProperty('duration')
print('%s,%s,%s,%s,%s,%s' %( context.getProperty('status'), context.getProperty('all_tests'),
                          context.getProperty('failures'), context.getProperty('errors'),
                          context.getProperty('skips'), seconds))
return printed
