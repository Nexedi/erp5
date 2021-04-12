portal = context.getPortalObject()
domain = context.getDefaultEventPathDestinationValue()

def redirect(message):
  return context.Base_redirect(keep_items={'portal_status_message': context.Base_translateString(message)})

event_path = context.getDefaultEventPathValue()

if domain is None:
  return redirect('Recipients must be defined')

if event_path.getEventPortalType() is None:
  return redirect('Event Type must be defined')

if event_path.getSourceValue() is None:
  return redirect('Sender must be defined')

if event_path.getResourceValue() is None:
  return redirect('Notification Message must be defined')

if (not event_path.getResourceReference()) \
   or portal.notification_message_module.NotificationTool_getDocumentValue(
      event_path.getResourceReference()) is None:
  return redirect('Notification Message must be validated')

event_path = context.getDefaultEventPathValue(portal_type="Event Path")
method_kw = {
    'event_path': event_path.getRelativeUrl(),
    'keep_draft': keep_draft,
}
portal.portal_catalog.activate(activity='SQLQueue').searchAndActivate(
  "Entity_createEventFromDefaultEventPath",
  selection_domain={domain.getParentId(): ('portal_domains', domain.getRelativeUrl())},
  method_kw=method_kw)
return redirect('Events are being created in background')
