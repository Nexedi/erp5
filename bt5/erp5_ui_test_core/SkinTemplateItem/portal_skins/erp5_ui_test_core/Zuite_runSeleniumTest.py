"""
  Generate a Zuite (if necessary), create/update the test and redirect to the selenium test created/updated
  url, web_page or web_page_reference must be set for it to work (or the context should be the Web Page in question)
"""
test_list = []
count = 0
portal = context.getPortalObject()
for url in url_list:
  count += 1
  if "http" not in url:
    # local content
    data = portal.restrictedTraverse(url).TestPage_viewSeleniumTest(
      manager_username=manager_username,
      manager_password=manager_password,
    )
  else:
    data = context.Zuite_urlRead(url, safe_return=1)
  test_list.append((data, '%s %s' % (count, url)),)

return context.Zuite_createAndLaunchSeleniumTest(test_list=test_list,
                                                 zuite_id=zuite_id)
