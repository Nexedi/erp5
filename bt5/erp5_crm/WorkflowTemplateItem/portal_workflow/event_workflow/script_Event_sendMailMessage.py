"""Really send the mail message.

This script has proxy role, for 'Use Mailhost services' permission required
by event.send
"""

event = state_change['object']
portal = state_change.getPortal()

if event.getPortalType() in ('Mail Message', ):
  send_mail = portal.portal_workflow.getInfoFor(event, 'send_mail',
                                                wf_id='event_workflow')
  if send_mail:
    if event.getSource():
      event.send()
    else:
      event.send(mfrom=portal.portal_preferences.getPreferredEventSenderEmail())
