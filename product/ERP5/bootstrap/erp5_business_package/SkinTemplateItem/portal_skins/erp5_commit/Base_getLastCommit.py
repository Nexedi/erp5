from operator import attrgetter

portal = context.getPortalObject()

commit_tool = portal.portal_commits
# Get all commits in commit tool
commit_list = commit_tool.objectValues(portal_type='Business Commit')

lastest_commit = max(commit_list, key=attrgetter('creation_date'))

if latest_commit is None:
  return ''

return latest_commit.title
