"""Base_getFormIdForWorkflowAction returns form_id of a form (dialog) used by `workflow_action`

This is not an UI script - it should be used in TALES expressions or called internally.

Developer Notes:

Format of Action returned by getFilteredActions['workflow'] = [{
  'available': True,
  'visible': True,
  'allowed': True,
  'link_target': None,
  'id': 'invalidate_action',
  'category': 'workflow',
  'name': 'Invalidate Action',
  'title': 'Invalidate Action',
  'url': 'https://softinst81338.host.vifib.net/erp5/web_site_module/renderjs_runner/foo_module/27/Base_viewWorkflowActionDialog?workflow_action=invalidate_action',
  'transition': <TransitionDefinition at /erp5/portal_workflow/foo_workflow/id_form_dict/invalidate_action>,
  'icon': ''}, ... ]
"""
action_tool = context.getPortalObject().portal_actions
id_form_dict = dict()

result_list = ()
if uids is not None:
  result_list = context.getPortalObject().portal_catalog(uid=uids)
else:
  result_list = context.Base_searchUsingFormIdAndQuery(form_id, query)

for result in result_list:
  for action in action_tool.listFilteredActionsFor(result.getObject()).get('workflow', []):
    action_form_id = action['url'].rsplit('/', 1)[1].split('?')[0]
    id_form_dict[action['id']] = action_form_id
    if workflow_action == action['id']:
      return action_form_id  # early return for performance reasons

if not workflow_action and len(id_form_dict) == 1:
  # if we have only one possible workflow transition we suppose it is the default one
  return id_form_dict.items()[0][1]

# if we have no idea what workflow form we should use - just use ~~the default one~~ nothing
return ""
