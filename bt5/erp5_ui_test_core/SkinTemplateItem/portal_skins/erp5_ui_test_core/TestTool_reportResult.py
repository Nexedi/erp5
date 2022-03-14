# This script is called when you invoke a browser with "?auto=true" to portal_tests.
# FIXME: this script should send the result by email.

get = request.form.get

# Summary.
result = ['Report on Functional Tests', '']
result.append('Passed: %s' % (get('result').lower() == 'passed' and 'Yes' or 'No'))
result.append('Total Time: %s' % get('totalTime'))
result.append('Passed Tests: %s' % get('numTestPasses'))
result.append('Failed Tests: %s' % get('numTestFailures'))
result.append('Passed Commands: %s' % get('numCommandPasses'))
result.append('Failed Commands: %s' % get('numCommandFailures'))
result.append('Commands with Errors: %s' % get('numCommandErrors'))
result.append('')

# Details.
table_list = []
for key in list(request.form.keys()):
  if key.startswith('testTable'):
    prefix, num = key.split('.')
    table_list.append((prefix, int(num)))
table_list.sort()
for table in table_list:
  key = '%s.%d' % table
  html = get(key)

  # Ugly, but get the title somehow.
  i = html.index('<td')
  start = html.index('>', i) + 1
  end = html.index('<', start)
  title = html[start:end]

  # Count passes and failures.
  num_passed_commands = html.count('bgcolor="#cfffcf"', end)
  num_failed_commands = html.count('bgcolor="#ffcfcf"', end)
  result.append('%s: %d passed, %d failed' % (title, num_passed_commands, num_failed_commands))

return '\n'.join(result)
