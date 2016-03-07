other_file_list = []
if modified != 'none':
  other_file_list += modified.split(',')
if removed != 'none':
  other_file_list += removed.split(',')

added_file_list = added != 'none' and added.split(',') or ()

if added_file_list or other_file_list:
  context.getVcsTool().revertZODB(added_file_list=added_file_list, other_file_list=other_file_list)
  context.REQUEST.set('portal_status_message', 'Changes reverted successfully.')
else:
  context.REQUEST.set('portal_status_message', 'Nothing to revert.')

return context.BusinessTemplate_viewVcsStatus()
