test_result = sci['object']

state = 'failed'
if test_result.getStringIndex() == 'PASS' and test_result.getProperty('all_tests', 0) > 0:
  state = 'success'

test_result.activate(activity='SQLQueue').TestResult_annotateCommit(state)
