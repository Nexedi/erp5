from Products.ERP5Type.Log import log

log("Folder method received dialog_id, form_id, uids and {!s}".format(kwargs.keys()))

if 'has_changed' not in kwargs or kwargs['has_changed'] is None:
  message = "Did nothing."
else:
  if kwargs['has_changed']:
    message = "Data has changed."
  else:
    message = "Data the same."

return context.Base_redirect(form_id, keep_items={"portal_status_message": message})
