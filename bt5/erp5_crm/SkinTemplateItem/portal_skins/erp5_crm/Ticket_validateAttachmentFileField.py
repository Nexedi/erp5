"""
This validator prevents users to add attachments to an event
if this event doesn't support 'Embedded Files'.
"""
if not editor:
  return True
event_type = context.getPortalObject().portal_types[request.form.get('field_your_portal_type', None)]
if 'Embedded File' in event_type.getTypeAllowedContentTypeList():
  return True
return False
