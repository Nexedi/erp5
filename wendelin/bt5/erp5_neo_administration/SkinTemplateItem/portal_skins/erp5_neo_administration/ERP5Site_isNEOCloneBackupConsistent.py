"""
  Examine remote NEO clone lists results already saved in an Active Process.
"""
from Products.CMFActivity.ActiveResult import ActiveResult

active_result = ActiveResult()

# find latest Active Process
active_process = context.portal_catalog.getResultValue(
                           portal_type = 'Active Process',
                           title = 'NEO_Clone_check',
                           sort_on=(('modification_date', 'descending'),))
result_list  = [x.getResult() for x in active_process.getResultList()]

context.log("Check NEO consistency using %s" %active_process.getPath())

is_consistent = 1
for result in result_list:
  if result.startswith('PROBLEM:'):
    is_consistent = 0
    break

if not is_consistent:
  severity = 1
  summary = "NEO inconsistency report at %s" %active_process.getPath()
  detail = result 
else:
  severity = 0
  summary = "Nothing to do."
  detail = ""

# save as a result from alarm
active_result.edit(
  summary=summary, 
  severity=severity,
  detail=detail)
context.newActiveProcess().postResult(active_result)

return 1
