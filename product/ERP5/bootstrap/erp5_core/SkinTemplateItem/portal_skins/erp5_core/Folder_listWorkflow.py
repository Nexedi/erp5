"""Return items (ready to be used in listbox of listfield) of common workflows on documents defined by `form_id` and `query`.

:param form_id: {str} Form.ID of a form containing listbox to execute the query
:param query: {str} fulltext query
:param add_empty: {bool} First choice is empty

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
  'transition': <TransitionDefinition at /erp5/portal_workflow/foo_workflow/transition_dict/invalidate_action>,
  'icon': ''}, ... ]
"""
def formatDict(d, padding=0):
  if not isinstance(d, dict):
    return " " * padding + str(d)
  return "\n".join(" " * padding + key + ":" + formatDict(d[key], padding+4) for key in d)

action_tool = context.getPortalObject().portal_actions
translate = context.getPortalObject().Base_translateString
workflow_list = []

if add_empty:
  workflow_list.append((translate('Choose desired action.'), ''))

transition_dict = {}

for result in context.Base_searchUsingFormIdAndQuery(form_id, query):
  for action in action_tool.listFilteredActionsFor(result.getObject()).get('workflow', []):
    transition_dict[action['id']] = action['title']

if not transition_dict:
  workflow_list.append((translate("No state change possible"), ""))

if len(transition_dict) == 1:
  workflow_list = []  # if there is only one workflow possible - do not bother with an empty option

# transition_dict.items() is in form (id, title) but ERP5 requires (title, id) so we reverse
if transition_dict:
  workflow_list.extend((title, id) for id, title in sorted(transition_dict.items(), key=lambda x: x[1]))

return workflow_list
