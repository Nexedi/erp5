parameter_list = field.getTemplateField().get_value('default_params')

# Some document subobjects have a workflow, and so, can be only be deleted from some state
# If the listbox does not display them, do not add the state filter parameter
filter_portal_type_list = [x[1] for x in parameter_list if x[0] == 'portal_type']
if filter_portal_type_list:
  if sametype(filter_portal_type_list, ''):
    filter_portal_type_list = [filter_portal_type_list]
else:
  filter_portal_type_list = None

return parameter_list + context.Module_listWorkflowTransitionItemList(filter_portal_type_list=filter_portal_type_list)
