"""Return a list of Documents specified by `uid` which provide `workflow_id` transition."""

action_tool = context.getPortalObject().portal_actions

result_list = context.Base_searchUsingListbox(
  context.Base_getListbox(context.getPortalObject().REQUEST.get("form_id")), sort_on=sort_on, limit=limit, **kwargs)

if not workflow_action:
  # if we have no filter (=workflow action) we return back all documents
  return result_list

filtered_list = []
for document in (result.getObject() for result in result_list):
  for action in action_tool.listFilteredActionsFor(document).get('workflow', []):
    if action['id'] == workflow_action:
      filtered_list.append(document)
      break

return filtered_list
