portal_tests = container.portal_tests
if test_zuite_relative_url is not None:
  # we care for a specific test zuite
  portal_tests = portal_tests.restrictedTraverse(test_zuite_relative_url,\
                                                 portal_tests)
# remove test results from previous test runs
portal_tests.manage_delObjects([x.getId() \
          for x in portal_tests.objectValues('Zuite Results')])
print("OK")
return printed
