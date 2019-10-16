"""Returns info about a test result, a mapping containing:

  test_suite_relative_url: relative url of test suite
  repository_dict: for each test suite repository, keyed by buildout section id:
     revision: commit sha
     repository_url: git url of the repository
     commits_count: number of commits

returns None if test suite cannot be found.
"""
portal = context.getPortalObject()

test_suite_list = portal.portal_catalog(
  portal_type='Test Suite',
  validation_state=('validated', 'invalidated'),
  title={'query': context.getTitle(), 'key': 'ExactMatch'})

if not test_suite_list:
  return None

test_suite = sorted(
  [test_suite.getObject() for test_suite in test_suite_list],
  key=lambda test_suite: test_suite.getValidationState() == 'validated')[-1]


# decode the reference ( ${buildout_section_id}=${number of commits}-${hash},${buildout_section_id}=${number of commits}-${hash} )
repository_dict = {}
if context.getReference() and '-' in context.getReference(): # tolerate invalid references, especially for tests
  for repository_string in context.getReference().split(','):
    buildout_section_id_and_commits_count, revision = repository_string.split('-')
    buildout_section_id, commits_count = buildout_section_id_and_commits_count.split('=')
    repository_dict[buildout_section_id] = {
        'revision': revision,
        'commits_count': int(commits_count),
    }

# add information about test suite repositories
for test_result_repository in test_suite.contentValues(portal_type='Test Suite Repository'):
  buildout_section_id = test_result_repository.getBuildoutSectionId()
  # NodeTestSuite.revision strip trailing -repository
  buildout_section_id = buildout_section_id[:-11] if buildout_section_id.endswith('-repository') else buildout_section_id
  repository_data = repository_dict.setdefault(buildout_section_id, {})
  repository_data['repository_url'] = test_result_repository.getGitUrl()
  repository_data['connector_relative_url'] = test_result_repository.getDestination()

if REQUEST:
  REQUEST.RESPONSE.setHeader('content-type', 'application/json; charset=utf-8')

return {
    'test_suite_relative_url': test_suite.getRelativeUrl(),
    'repository_dict': repository_dict,
}
