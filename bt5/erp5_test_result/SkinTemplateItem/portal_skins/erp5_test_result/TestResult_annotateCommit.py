"""Annotate a commit with state of the test (running, canceled, success, failed)
"""
portal = context.getPortalObject()

portal_absolute_url = portal.ERP5Site_getAbsoluteUrl()

test_suite_data = context.TestResult_getTestSuiteData()
if test_suite_data:
  for repository_info in test_suite_data['repository_dict'].values():
    connector_url = repository_info['connector_relative_url']
    if connector_url:
      portal.restrictedTraverse(connector_url).postCommitStatus(
          repository_info['repository_url'],
          repository_info['revision'],
          state,
          '%s/%s' % ( portal_absolute_url, context.getRelativeUrl() ),
          context.getTitle()
      )
