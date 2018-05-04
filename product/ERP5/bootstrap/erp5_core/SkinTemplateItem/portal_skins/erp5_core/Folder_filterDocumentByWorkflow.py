"""Return a list of Documents specified by `uid` which provide `workflow_id` transition."""

portal_catalog = context.getPortalObject().portal_catalog
action_tool = context.getPortalObject().portal_actions

if not uid:
  return []

document_list = [result.getObject() for result in portal_catalog.searchResults(uid=uid, sort_on=sort_on, limit=limit)]

if not workflow_action:
  # if we have no filter (=workflow action) we return back all documents
  return document_list

filtered_list = []
for document in document_list:
  for action in action_tool.listFilteredActionsFor(document).get('workflow', []):
    if action['id'] == workflow_action:
      filtered_list.append(document)
      break

return filtered_list
