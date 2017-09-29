import json

portal = context.getPortalObject()

count_list = []
state_dict = {
  "submitted": "Support Request to Open",
  "draft": "Support Request to Submit",
  "validated": "Support Request to Close",
  "suspended": "Suspended Support Requests"
}

# XXX hardcoded, these lines below reflect portal_workflow/ticket_workflow worklists
count_list.append({
  'query_string': 'portal_type:"Support Request" AND simulation_state:"draft" AND local_roles:"Owner"',
  'action_name': state_dict["draft"],
  'action_count': portal.support_request_module.countFolder(portal_type="Support Request", simulation_state="draft", local_roles="Owner")[0][0]})
count_list.append({
  'query_string': 'portal_type:"Support Request" AND simulation_state:"submitted" AND local_roles:"Assignor"',
  'action_name': state_dict["submitted"],
  'action_count': portal.support_request_module.countFolder(portal_type="Support Request", simulation_state="submitted", local_roles="Assignor")[0][0]})
count_list.append({
  'query_string': 'portal_type:"Support Request" AND simulation_state:"validated" AND local_roles:("Assignee" OR "Assignor")',
  'action_name': state_dict["validated"],
  'action_count': portal.support_request_module.countFolder(portal_type="Support Request", simulation_state="validated", local_roles=("Assignee", "Assignor"))[0][0]})
count_list.append({
  'query_string': 'portal_type:"Support Request" AND simulation_state:"suspended" AND local_roles:("Assignee" OR "Assignor")',
  'action_name': state_dict["suspended"],
  'action_count': portal.support_request_module.countFolder(portal_type="Support Request", simulation_state="suspended", local_roles=("Assignee", "Assignor"))[0][0]})

return json.dumps(count_list)
