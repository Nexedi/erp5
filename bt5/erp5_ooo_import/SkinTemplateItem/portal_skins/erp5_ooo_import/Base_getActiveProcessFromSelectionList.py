'''
get the list of active process from the selection
'''

user_name = context.portal_membership.getAuthenticatedMember().getId()
module_title=context.getTitle()

active_process_dict = {}

selection_param_list = context.portal_selections.getSelectionParamsFor('file_import_parameters_selection').items()

for (x,y) in selection_param_list:
  if x.startswith('portal_activities'):
    if y['import_module']==module_title and y['import_user_name']==user_name:
      active_process_dict[x] = "Module %s, imported at %s by %s" % (y['import_module'], y['import_date_time'], y['import_user_name'])

active_process_list = [(y,x) for (x,y) in active_process_dict.items()]

return sorted(active_process_list, key=lambda item: item[1], reverse=True)
