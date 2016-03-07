portal_tests = container.portal_tests
if test_zuite_relative_url is not None:
  # we care for a specific test zuite
  portal_tests = portal_tests.restrictedTraverse(test_zuite_relative_url,
                                                 portal_tests)

results = portal_tests.objectValues('Zuite Results')
#results.sort()

if not results:
  return None

return results[len(results) - 1].getId()
