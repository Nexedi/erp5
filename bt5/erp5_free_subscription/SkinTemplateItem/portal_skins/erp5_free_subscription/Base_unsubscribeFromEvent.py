"""This script is indented to be used in email as a link for people to 
unsubscribe from a mailling
"""
portal = context.getPortalObject()
request = context.REQUEST
event_id = request['id']

user = portal.ERP5Site_getAuthenticatedMemberPersonValue()
# If we have a logged in user it's probably a backoffice agent.
if user is None:
  # If the referer contains the url of the event we are probably viewing the event
  # from ERP5 interface. We do not want to mark the event as delivered in that case
  # It can also be from fckeditor, in this case we don't have the event url in REFERER.
  if not ( ('/event_module/%s' % event_id) in request.HTTP_REFERER or 'fckeditor' in request.HTTP_REFERER):
    if portal.Base_getHMACHexdigest(portal.Base_getEventHMACKey(), event_id) != request["hash"]:
      from zExceptions import Unauthorized
      raise Unauthorized()
    
    portal.portal_activities.activate(
      activity="SQLQueue").Base_createFreeSubscriptionRequest(
          event_id=request['id'], 
          hmac=request["hash"])

# serve the web-page that will display a "Sucessfully unsubscribe" message
return context.index_html(request, request.RESPONSE, format=None)
