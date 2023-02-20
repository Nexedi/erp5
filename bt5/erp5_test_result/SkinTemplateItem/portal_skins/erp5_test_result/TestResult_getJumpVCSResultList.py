"Jump to gitlab or gitweb web interface to view commit"

from Products.PythonScripts.standard import Object

test_suite_data = context.TestResult_getTestSuiteData()
result_list = []

def makeVCSLink(repository_url, revision):
  # https://user:pass@lab.nexedi.cn/user/repo.git -> https://user:pass@lab.nexedi.cn/user/repo/commit/hash
  if 'lab.nexedi' in repository_url and repository_url.endswith('.git'):
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
  
for repository in test_suite_data['repository_dict'].values():
  result_list.append(
    makeVCSLink(
      repository['repository_url'],
      repository['revision']))

if len(result_list) == 1:
  from zExceptions import Redirect
  raise Redirect(result_list[0].getListItemUrl())

return result_list
