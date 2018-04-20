from Products.ERP5Type.Log import log

log("Folder method received dialog_id, form_id, uids and {!s}".format(kwargs.keys()))

return context.Base_redirect(form_id, keep_items={"portal_status_message": "Did nothing."})
