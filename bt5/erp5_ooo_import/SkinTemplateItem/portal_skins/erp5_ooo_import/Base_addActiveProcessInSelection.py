'''
  Add an active process in the selection
'''
user_name = context.portal_membership.getAuthenticatedMember().getId()

active_process_info = {
  'import_module': context.getTitle(),
  'import_user_name': user_name,
  'import_date_time': DateTime(),
}

selection = context.portal_selections.getSelectionParamsFor('file_import_parameters_selection')
selection[active_process_path] = active_process_info
context.portal_selections.setSelectionParamsFor('file_import_parameters_selection', selection)
