import six
portal = context.getPortalObject()
getWorkflowValueListFor = portal.portal_workflow.getWorkflowValueListFor
translateString = portal.Base_translateString
state_variable_set = set()
add = state_variable_set.add
type_state_variable_workflow_dict = {}
type_workflow_state_count_dict_dict = {}
workflow_translated_title_dict = {}
workflow_translated_state_title_dict = {}
portal_type_translated_title_dict = {}
for portal_type in context.allowedContentTypes():
  portal_type_id = portal_type.getId()
  portal_type_translated_title_dict[portal_type_id] = translateString(portal_type.getTitle())
  for workflow in getWorkflowValueListFor(portal_type_id):
    state_list = workflow.getStateValueList()
    if len(state_list) > 1:
      state_var = workflow.getStateVariable()
      workflow_id = workflow.getId()
      workflow_translated_title_dict[workflow_id] = translateString(workflow.title)
      type_state_variable_workflow_dict[(portal_type_id, state_var)] = workflow_id
      state_count_dict = type_workflow_state_count_dict_dict.setdefault((portal_type_id, workflow_id), {})
      translated_state_title_dict = workflow_translated_state_title_dict.setdefault(workflow_id, {})
      for state in state_list:
        # TODO: support workflow-specific translations
        state_id = state.getReference()
        translated_state_title_dict[state_id] = translateString(state.title)
        state_count_dict[state_id] = 0
      add(state_var)
column_list = ['portal_type'] + list(state_variable_set)
search_folder_kw = {}
if use_selection:
  selection_kw = portal.portal_selections.getSelectionParamsFor(selection_name).copy()
  selection_kw.pop('limit', None)
  search_folder_kw['query'] = portal.portal_catalog.getSQLCatalog().buildQuery(selection_kw)
select_dict = dict.fromkeys(column_list)
select_dict['count'] = 'count(*)'
for line in context.searchFolder(group_by=column_list, select_dict=select_dict, **search_folder_kw):
  portal_type = line.portal_type
  count = line.count
  for state_variable in state_variable_set:
    workflow = type_state_variable_workflow_dict.get((line.portal_type, state_variable))
    state = getattr(line, state_variable)
    if workflow is None:
      assert not state, (portal_type, state_variable, state)
      continue
    state_count_dict = type_workflow_state_count_dict_dict[(portal_type, workflow)]
    state_count_dict[state] = count + state_count_dict[state]
listbox = []
append = listbox.append
for (portal_type, workflow), state_count_dict in sorted(six.iteritems(type_workflow_state_count_dict_dict), key=lambda x: x[0]):
  if sum(state_count_dict.values()):
    append({
      'translated_portal_type': '%s - %s' % (portal_type_translated_title_dict[portal_type], workflow_translated_title_dict[workflow]),
      'state' : '',
      'count' : '',
    })
    translated_state_title_dict = workflow_translated_state_title_dict[workflow]
    for state, count in sorted(six.iteritems(state_count_dict), key=lambda x: x[0]):
      if count:
        append({
          'translated_portal_type': '',
          'state': translated_state_title_dict[state],
          'count': count,
        })
portal.Base_updateDialogForm(listbox=listbox, empty_line_number=0)
return context.Folder_viewWorkflowReport()
