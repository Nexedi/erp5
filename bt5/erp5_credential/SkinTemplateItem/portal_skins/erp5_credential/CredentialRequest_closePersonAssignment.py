"""Close all person assignment
Parameters:
role -- Role category item (List of String, default: [])
comment -- Workflow transition comment (String, default: "")
Proxy:
Assignor -- only assignor manage assignment. Needed this proxy for auto accept
Return opened assignment list
"""

person = context.getDestinationDecisionValue(portal_type="Person")

# Check current assignment

current_assignment_list = person.searchFolder(portal_type="Assignment",
                                              validation_state="open")
open_assignment = []
for assignment in current_assignment_list:
  assignment = assignment.getObject()
  if assignment.getRole() in role:
    assignment.close(comment)
  else:
    open_assignment.append(assignment)
return open_assignment
