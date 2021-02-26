"""
  test_list is composed by [(full_test_html , title), ]

"""

zuite = context.getPortalObject().portal_tests.Zuite_addZuite(zuite_id)

for text, title in test_list:
  zuite.Zuite_addTest(None, title, text)

ZELENIUM_BASE_URL = "portal_tests/%s/core/TestRunner.html?auto=true&test=../test_suite_html&resultsUrl=../postResults"

return zuite.Base_redirect(ZELENIUM_BASE_URL % zuite_id)
