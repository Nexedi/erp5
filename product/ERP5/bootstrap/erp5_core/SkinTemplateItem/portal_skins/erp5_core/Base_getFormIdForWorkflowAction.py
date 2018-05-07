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

for result in context.Base_searchUsingFormIdAndQuery(form_id, query):
  for action in action_tool.listFilteredActionsFor(result.getObject()).get('workflow', []):
    id_form_dict[action['id']] = action['url'].rsplit('/', 1)[1].split('?')[0]

if not workflow_action and len(id_form_dict) == 1:
  # if we have only one possible workflow transition we suppose it is the default one
  return id_form_dict.items()[0][1]

if workflow_action in id_form_dict:
  # if the workflow_action is done and we found it then return related form dialog
  return id_form_dict[workflow_action]

# if we have no idea what workflow form we should use - just use ~~the default one~~ nothing
return ""
