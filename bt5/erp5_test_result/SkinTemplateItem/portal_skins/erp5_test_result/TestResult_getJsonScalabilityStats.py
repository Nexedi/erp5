from Products.PythonScripts.standard import Object
import json

# Get result lines
test_result_lines = context.objectValues(portal_type="Test Result Line", sort_on='int_index')

# Create a dict containing stats for each test
tests = []
count = 0
for tl in test_result_lines:
  # Get and parse stdout to a dict
  stdout = tl.getProperty('stdout')
  if stdout:
    count = count + 1
    stdout_lines = filter(None, stdout.split('\n'))
    current_stats = dict( [(l.split("=")[0].replace(" ", "_"), \
                     l.split("=")[1].isdigit() and int(l.split("=")[1]) or str(l.split("=")[1])) \
                     for l in stdout_lines ])

    tests.append(current_stats)

test_suite = context.getPortalObject().test_suite_module.searchFolder(title=context.getTitle())[0]

xs = map(int, test_suite.getGraphCoordinate())


return json.dumps({"test": tests, "xs": xs})
