task_report = state_change['object']
portal = task_report.getPortalObject()

# Notify the requester.
source_person = task_report.getSourceValue(portal_type="Person")
destination_decision_person = task_report.getDestinationDecisionValue(portal_type="Person")
if destination_decision_person is None:
  destination_decision_person = task_report.getDestinationValue(portal_type="Person")

# We send a message only if the requester have an email and
# the assignee is a user that can view the task report.
if source_person is not None \
     and destination_decision_person is not None \
     and destination_decision_person.getDefaultEmailText() \
     and destination_decision_person.Person_getUserId():
  if portal.acl_users.searchUsers(id=source_person.Person_getUserId(), exact_match=True):
    message = """
%s has finished the task report titled with %s.
Please look at this URL:
%s/%s
""" % (source_person.getTitle(), task_report.getTitle(),
       task_report.ERP5Site_getAbsoluteUrl(), task_report.getRelativeUrl())
    portal.portal_notifications.sendMessage(sender=source_person, recipient=destination_decision_person,
                                            subject="Task Report Finished", message=message)
