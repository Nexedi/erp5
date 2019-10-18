"""Annotate a commit with state of the test (running, canceled, success, failed)
"""
import re
portal = context.getPortalObject()

portal_absolute_url = portal.ERP5Site_getAbsoluteUrl()


def getTestResultStateForTestSuiteRepository(test_result_line_pattern_re):
  """Compute the state for this test repository.

  This is used in test results like SLAPOS-EGG-TEST where we run in the
  same test suite tests for multiple more-or-less independent repositories.
  We don't want to mark commits from all repositories failed when only one
  test as a problem.
  On test suite repository, we define the pattern of test lines to consider,
  this is used here to evaluate this repository only based on the result
  of the individual test result lines.
  """
  if test_result_line_pattern_re:
    # state of test result lines matching the pattern.
    return 'success' if {'PASSED'} == {
        test_result_line.getStringIndex() for test_result_line
        in context.contentValues(portal_type='Test Result Line')
        if test_result_line_pattern_re.search(test_result_line.getTitle())
    } else 'failed'
  return state # global state of the test result.

test_suite_data = context.TestResult_getTestSuiteData()
if test_suite_data:
  for repository_info in test_suite_data['repository_dict'].values():
    connector_url = repository_info['connector_relative_url']
    if connector_url:
      portal.restrictedTraverse(connector_url).postCommitStatus(
          repository_info['repository_url'],
          repository_info['revision'],
          getTestResultStateForTestSuiteRepository(
              re.compile(repository_info['test_result_line_pattern'])),
          '%s/%s' % ( portal_absolute_url, context.getRelativeUrl() ),
          context.getTitle()
      )
