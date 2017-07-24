from Products.CMFActivity.ActiveResult import ActiveResult

# TODO: Fetch execution context (eg. Data Notebook) and execute
# the script in this context, instead of on each Data Notebook Line
try:
  result = context.getDefaultNotebookCodeValue()()
except Exception:
  pass
# XXX: Support error reporting!!
if active_process is not None:
  active_result = ActiveResult()
  active_result.edit(
    detail=result)

  active_process_document = context.restrictedTraverse(active_process)
  active_process_document.postResult(active_result)
return result
