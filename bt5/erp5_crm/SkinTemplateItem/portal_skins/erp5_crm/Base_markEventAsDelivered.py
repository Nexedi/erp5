portal = context.getPortalObject()
if portal.Base_getHMACHexdigest(portal.Base_getEventHMACKey(), event_id) != hmac:
  from zExceptions import Unauthorized
  raise Unauthorized

event = portal.event_module[event_id]
if portal.portal_workflow.isTransitionPossible(event, 'deliver'):
  event.deliver()
