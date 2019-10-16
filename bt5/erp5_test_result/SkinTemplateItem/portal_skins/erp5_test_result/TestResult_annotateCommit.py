"""Annotate a commit with state of the test (running, canceled, success, failed)
"""
portal = context.getPortalObject()

portal_url = portal.ERP5Site_getAbsoluteUrl()
test_result_relative_url = context.getRelativeUrl()
test_result_relative_id = context.getId()
test_result_reference = context.getReference()

test_suite_data = context.TestResult_getTestSuiteData()
if test_suite_data:
  for repository_info in test_suite_data['repository_dict'].values():
    connector_url = repository_info['connector_relative_url']
    if connector_url:
      connector = portal.restrictedTraverse(connector_url)
      connector.postCommitStatus(
          repository_info['repository_url'],
          repository_info['revision'],
          state,
          connector.getTestResultUrlTemplate().format(
              portal_url=portal_url,
              test_result_relative_url=test_result_relative_url,
              test_result_relative_id=test_result_relative_id,
              test_result_reference=test_result_reference),
          context.getTitle()
      )
