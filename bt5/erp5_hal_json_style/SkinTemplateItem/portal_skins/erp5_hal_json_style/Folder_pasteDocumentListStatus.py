portal = context.getPortalObject()
Base_translateString = portal.Base_translateString
translate = Base_translateString

if not listbox_uid:
  return context.Base_redirect(keep_items={
    'portal_status_message': translate("Please select one or more items first."),
    'portal_status_level': "warning"})

copy_data = context.manage_copyObjects(uids=listbox_uid)
context.manage_pasteObjects(copy_data)

message = Base_translateString("Pasted.")
return context.Base_redirect(form_id, keep_items={"portal_status_message": str(message)})
