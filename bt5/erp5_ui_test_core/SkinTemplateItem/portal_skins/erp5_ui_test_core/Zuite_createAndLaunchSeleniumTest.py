"""
  test_list is composed by [(full_test_html , title), ]

"""

zuite = context.getPortalObject().portal_tests.Zuite_addZuite(zuite_id)

for text, title in test_list:
  zuite.Zuite_addTest(None, title, text)

return zuite.Base_redirect("portal_tests/%s/core/TestRunner.html?auto=true&test=..%%2Ftest_suite_html&resultsUrl=..%%2FpostResults" % zuite_id)
