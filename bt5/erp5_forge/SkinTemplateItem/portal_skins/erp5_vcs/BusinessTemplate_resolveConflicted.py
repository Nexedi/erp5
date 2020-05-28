request = context.REQUEST
try:
  files_list = request['uids']
except KeyError:
  message = 'You MUST select at least one file.'
else:
  context.getVcsTool().resolved(files_list)
  message = 'Conflicted files resolved successfully.'

request.set("portal_status_message", message)
return context.BusinessTemplate_viewConflicted()
