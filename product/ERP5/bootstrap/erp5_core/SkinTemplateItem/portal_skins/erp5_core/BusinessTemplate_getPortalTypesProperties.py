context.getPortalTypesProperties()

REQUEST = context.REQUEST

if REQUEST is not None:
  return context.Base_redirect(
    REQUEST.get("form_id", "view"),
    keep_items={'portal_status_message': 'Portal Types Properties Updated'})
