from Products.CMFActivity.ActiveResult import ActiveResult
active_result = ActiveResult()
severity = len(error_list)
if severity == 0:
  summary = "No error"
else:
  summary = "Error"
active_result.edit(summary=summary, severity=severity, detail='\n'.join(error_list))
return active_result
