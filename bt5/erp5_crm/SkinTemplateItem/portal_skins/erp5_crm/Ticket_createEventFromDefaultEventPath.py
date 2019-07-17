portal = context.getPortalObject()
domain = context.getDefaultEventPathDestinationValue()

if domain is None:
  message = 'Recipients must be defined'
else:
  event_path = context.getDefaultEventPathValue(portal_type="Event Path")
  method_kw = {'event_path': event_path.getRelativeUrl(),
   'keep_draft': keep_draft}
  portal.portal_catalog.activate(activity='SQLQueue').searchAndActivate(
    "Entity_createEventFromDefaultEventPath",
    selection_domain={domain.getParentId(): ('portal_domains', domain.getRelativeUrl())},
    method_kw=method_kw)
  message = 'Events are being created in background'

return context.Base_redirect(keep_items={'portal_status_message': context.Base_translateString(message)})
