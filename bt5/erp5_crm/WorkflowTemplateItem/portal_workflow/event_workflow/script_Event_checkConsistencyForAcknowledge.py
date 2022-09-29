from Products.ERP5Type.Core.Workflow import ValidationFailed
from Products.ERP5Type.Message import translateString

container.Event_checkConsistency(sci)

portal = sci.getPortal()
portal_workflow = portal.portal_workflow
event = sci['object']

follow_up_ticket_type = portal_workflow.getInfoFor(event,
                                                   'follow_up_ticket_type',
                                                   wf_id='event_workflow')

follow_up_ticket_title = portal_workflow.getInfoFor(event,
                                                    'follow_up_ticket_title',
                                                    wf_id='event_workflow')

if follow_up_ticket_type not in ["", None] and \
     follow_up_ticket_title not in ["", None]:
  return

if not event.getFollowUp():
  raise ValidationFailed(translateString('Follow up must be set to acknowledge an Event.'))
