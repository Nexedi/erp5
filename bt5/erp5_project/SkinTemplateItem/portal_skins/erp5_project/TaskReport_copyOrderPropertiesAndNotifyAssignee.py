if related_simulation_movement_path_list is None:
  raise RuntimeError('related_simulation_movement_path_list is missing. Update ERP5 Product.')

if REQUEST is not None:
  from zExceptions import Unauthorized
  raise Unauthorized(script.id)

task_report = context
portal = task_report.getPortalObject()

# First, copy Order properties
task_report.PackingList_copyOrderProperties()

related_order = task_report.getCausalityValue()

if task_report.getSimulationState() == 'draft':
  task_report.edit(
    comment=related_order.getComment(),
    description = related_order.getDescription(),
    delivery_mode=related_order.getDeliveryMode(),
    incoterm=related_order.getIncoterm(),
    source_administration_value=related_order.getSourceAdministrationValue(),
    destination_decision_value=related_order.getDestinationDecisionValue(),
    title=related_order.getTitle()
  )

# If security definitions are implemented on the packing list, it is time to apply them
task_report.assignRoleToSecurityGroup()

# Notify the requester.
source_person = task_report.getSourceValue(portal_type="Person")
destination_decision_person = task_report.getDestinationDecisionValue(portal_type="Person")
if destination_decision_person is None:
  destination_decision_person = task_report.getDestinationValue(portal_type="Person")

# We send a message only if the requester has an email
# and the assignee has one too and is an user that can view the task report.
if (
      source_person is not None and
      source_person.getDefaultEmailText() and # XXX Add unit test: check if task confirmation works if assignee has no mail
      destination_decision_person is not None and
      destination_decision_person.getDefaultEmailText() and
      destination_decision_person.Person_getUserId()
    ):
  if portal.acl_users.searchUsers(id=source_person.Person_getUserId(), exact_match=True):
    message = """A new task has been assigned to you by %(assignor)s.

This task is named: %(title)s

Description:
%(description)s

Start Date: %(start_date)s
Stop Date: %(stop_date)s

Please visit ERP5: %(url)s
""" % {
       'assignor': destination_decision_person.getTitle(),
       'title'   : task_report.getTitle(),
       'url'     : '%s/%s/view' % (task_report.ERP5Site_getAbsoluteUrl(),
                              task_report.getRelativeUrl()),
       'description' : task_report.getDescription(),
       'start_date': task_report.getStartDate().Date(),
       'stop_date': task_report.getStopDate().Date(),
      }
    portal.portal_notifications.sendMessage(sender=destination_decision_person,
                                            recipient=source_person,
                                            subject="[ERP5 Task] %s" % task_report.getTitle(),
                                            message=message)

task_report.Delivery_confirm()
