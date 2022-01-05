"""Create an assignment for the person depending credential request configuration
Proxy: Assignor -- allow to update the related assignment"""

# check the script is not called from a url
if REQUEST is not None:
  return None

person = context.getDestinationDecisionValue(portal_type="Person")
organisation = context.getDestinationDecisionValue(portal_type="Organisation")

#Look on current assignment
old_role_list = context.portal_categories.role.getCategoryChildLogicalPathItemList()[1:]
#old_role_list look like [['title','logical_path'],]
old_role_list = [category[1] for category in old_role_list]
for role in context.getRoleList():
  old_role_list.remove(role)

#Close old assignment
open_assignment_list = context.CredentialRequest_closePersonAssignment(old_role_list)

#Initialisation
assignment_duration = context.portal_preferences.getPreferredCredentialAssignmentDuration()
today = DateTime()
if assignment_duration < 0:
  delay = None
  start_date = None
else:
  delay = today+assignment_duration
  start_date = today - 1


current_assignment_list = {}
for assignment in open_assignment_list:
  role = assignment.getRole()
  if role in current_assignment_list:
    current_assignment_list[role].append(assignment)
  else:
    current_assignment_list[role] = [assignment]

organisation_url = organisation is not None and organisation.getRelativeUrl() or None
for role in context.getRoleList():
  if role in current_assignment_list:
    #Update assignment
    for assignment in current_assignment_list[role]:
      assignment.update()
      assignment.edit(site = context.getSite(),
                      activity = context.getActivityList(),
                      function = context.getFunctionList(),
                      destination = organisation_url,
                      stop_date=delay)
      assignment.open()
  else:
    #Create assignment
    assignment = person.newContent(
        portal_type='Assignment',
        title = '%s %s Assignment' % (context.getSite('').capitalize(), role.capitalize()),
        role = role,
        site = context.getSite(),
        activity = context.getActivityList(),
        function = context.getFunctionList(),
        group = context.getGroupList(),
        destination = organisation_url,
        start_date = start_date,
        stop_date = delay)

    assignment.open()
