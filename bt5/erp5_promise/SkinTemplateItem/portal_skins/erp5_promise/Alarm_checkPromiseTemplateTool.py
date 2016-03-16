from Products.CMFActivity.ActiveResult import ActiveResult

portal = context.getPortalObject()
promise_repository = portal.getPromiseParameter('portal_templates', 'repository')

if promise_repository is None:
  return

if promise_repository:
  promise_repository_list = promise_repository.split()
  promise_repository_list.sort()
else:
  promise_repository_list = []

repository_list = portal.portal_templates.getRepositoryList()
repository_list.sort()

active_result = ActiveResult()

if repository_list != promise_repository_list:
  severity = 1
  summary = "Template tool not configured as expected"
  detail = '\n'.join(promise_repository_list)
else:
  severity = 0
  summary = "Nothing to do."
  detail = ""

active_result.edit(
  summary=summary, 
  severity=severity,
  detail=detail)


context.newActiveProcess().postResult(active_result)
