try:
  files_list = context.REQUEST['uids']
except KeyError:
  message = 'You MUST select at least one file.'
else:
  context.getVcsTool().resolved(files_list)
  message = 'Conflicted files resolved successfully.'

return context.BusinessTemplate_viewConflicted()
