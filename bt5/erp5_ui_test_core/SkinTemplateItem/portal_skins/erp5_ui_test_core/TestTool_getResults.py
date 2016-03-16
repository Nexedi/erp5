portal_tests = container.portal_tests
if test_zuite_relative_url is not None:
  # we care for a specific test zuite
  portal_tests = portal_tests.restrictedTraverse(test_zuite_relative_url,
                                                 portal_tests)

results = portal_tests.objectValues('Zuite Results')
if not results:
  return None

# Selenium results tests are just named "testTable.1", "testTable.2" and so forth.
# We replace this by the path of the test, this way we can easily see which test has failed.
html = results[len(results) - 1].index_html()
for idx, test_case in enumerate(portal_tests.listTestCases()):
  html = html.replace('>testTable.%s</a>' % (idx + 1), '>%s</a>' % test_case['path'])

return html
