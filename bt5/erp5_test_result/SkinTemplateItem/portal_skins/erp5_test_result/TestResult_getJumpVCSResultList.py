"Jump to gitlab or gitweb web interface to view commit"

portal = context.getPortalObject()
test_suite_list = portal.portal_catalog(
  portal_type='Test Suite',
  validation_state=('validated', 'invalidated'),
  title={'query': context.getTitle(), 'key': 'ExactMatch'})

if not test_suite_list:
  return []

test_suite = sorted(
  [test_suite.getObject() for test_suite in test_suite_list],
  key=lambda test_suite: test_suite.getValidationState() == 'validated')[0]

# TODO: make this jump test suite

# decode the reference ( ${buildout_section_id}=${number of commits}-${hash},${buildout_section_id}=${number of commits}-${hash}, ... ) 
repository_dict = {}
for repository_string in context.getReference().split(','):
  repository_code, revision = repository_string.split('-')
  repository_dict[repository_code.split('=')[0]] = revision


result_list = []
from Products.PythonScripts.standard import Object

def makeVCSLink(repository_url, revision):
  # https://user:pass@lab.nexedi.cn/user/repo.git -> https://user:pass@lab.nexedi.cn/user/repo/commit/hash
  if 'lab.nexedi.cn' in repository_url and repository_url.endswith('.git'):
    repository_url = repository_url[:-len('.git')]
  if '@' in repository_url: # remove credentials
    scheme = repository_url.split(':')[0] 
    url = '%s://%s/commit/%s' % (scheme, repository_url.split('@')[1], revision )
  else:
    url = '%s/commit/%s' % (repository_url, revision )
  # gitweb for git.erp5.org
  if '/repos/' in url:
    url = url.replace('/repos/', '/gitweb/')
    url = url.replace('/commit/', '/commitdiff/')

  def getListItemUrl(*args, **kw):
    return url
  
  return Object(
    uid='new_',
    getUid=lambda: 'new_',
    getListItemUrl=getListItemUrl,
    repository=repository_url,
    revision=revision)
  
for repository in test_suite.contentValues(portal_type='Test Suite Repository'):
  result_list.append(
    makeVCSLink(
      repository.getProperty('git_url'),
      repository_dict[repository.getProperty('buildout_section_id')]))

if len(result_list) == 1:
  from zExceptions import Redirect
  raise Redirect(result_list[0].getListItemUrl())

return result_list
