import json

# Get result lines
test_result_lines = context.objectValues(portal_type="Test Result Line",
                                         sort_on="int_index")

# Create a dict containing stats for each test
tests = []
count = 0
results = {}
for tl in test_result_lines:
  # Get and parse stdout to a dict. this format ['Person: 372 doc/hour; SaleOrder: 132 doc/hour;']
  stdout = tl.getProperty('stdout')
  if stdout:
    count = count + 1
    stdout_lines = filter(None, stdout.split('\n'))
    for stdout_line in stdout_lines:
      tests_list = stdout_line.split(';')
      tests_list = [x for x in tests_list if x.strip()!='']
      for test in tests_list:
        test = test.strip()
        test_name = test.split(':')[0]
        test_documents_created = test.split(':')[1].replace('doc/hour', '').strip()
        # initial init
        if test_name not in list(results.keys()):
          results[test_name] = []
        results[test_name].append({'created_docs': test_documents_created,
                                   'duration':3600})

test_suite = context.getPortalObject().test_suite_module.searchFolder(title=context.getTitle())[0]

xs = map(int, test_suite.getGraphCoordinate())

# testnode usually runs multiple tests, for example for Person and Sale Order creation but
# viewer shows only one graph thus return only one test
tests = results[test_suite_name]

return json.dumps({"test": tests,
                   "xs": xs})
