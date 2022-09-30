"""
  Return list of Test Suites being tested by introspecting Test Result Lines
"""
test_suite_list = []
test_result_line_list = context.objectValues(
                          portal_type = 'Test Result Line',
                          sort_on="int_index")

if len(test_result_line_list) > 0:
  test_result_line = test_result_line_list[0]
  stdout = test_result_line.getProperty('stdout')
  for i in stdout.split(';'):
    test_suite_list.append(i.split(':')[0].strip())

# remote empty elements
test_suite_list = [x for x in test_suite_list if x.strip()!='']
return test_suite_list
