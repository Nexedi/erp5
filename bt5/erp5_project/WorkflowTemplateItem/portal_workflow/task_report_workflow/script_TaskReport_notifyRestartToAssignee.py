task_report = state_change['object']
portal = task_report.getPortalObject()

# Notify assignee
source_person = task_report.getSourceValue(portal_type="Person")
destination_decision_person = task_report.getDestinationDecisionValue(portal_type="Person")
if destination_decision_person is None:
  destination_decision_person = task_report.getDestinationValue(portal_type="Person")

# send notification only if the source have a valid email and is a user in the
# system that can view the task report
if source_person is not None \
      and destination_decision_person is not None\
      and source_person.getDefaultEmailText() \
      and source_person.Person_getUserId():
  if portal.acl_users.searchUsers(id=source_person.Person_getUserId(), exact_match=True):
    message = """
Restarted task has been assigned to you by %(assignor)s.

This task is named: %(title)s

Description:
%(comment)s

Start Date: %(start_date)s
Stop Date: %(stop_date)s

Please visit ERP5: %(url)s
""" % {
       'assignor': destination_decision_person.getTitle(),
       'title'   : task_report.getTitle(),
       'url'     : '%s/%s/view' % (task_report.ERP5Site_getAbsoluteUrl(),
                              task_report.getRelativeUrl()),
       'comment' : task_report.getComment(),
       'start_date': task_report.getStartDate().Date(),
       'stop_date': task_report.getStopDate().Date(),
      }
    portal.portal_notifications.sendMessage(sender=destination_decision_person, recipient=source_person,
                                          subject="[ERP5 Task]  Restarted Task Assigned to You ", message=message)
