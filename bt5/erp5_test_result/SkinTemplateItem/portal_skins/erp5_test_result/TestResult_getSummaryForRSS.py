test_result = context

result = []
p = result.append

if len([x for x in test_result.contentValues(portal_type='Test Result Node')
        if x.getSimulationState() == 'failed']):
  p('Result: %s (Building Failed)' % test_result.getStringIndex() )
else:
  p('Result: %s' % test_result.getStringIndex())

#p('Test Suite: %s' % test_result.getTitle())
p('Revision: %s' % test_result.getReference() or test_result.getIntIndex())
p('Launch Date: %s' % test_result.getStartDate())
comment = test_result.getProperty('comment')
if comment:
  p(comment)
p('')
p('All tests: %s, Failures: %s, Errors: %s, Skips: %s' % \
              (test_result.getProperty('all_tests'),
               test_result.getProperty('failures'),
               test_result.getProperty('errors'),
               test_result.getProperty('skips')))
p('')

return '<br>'.join(result)
