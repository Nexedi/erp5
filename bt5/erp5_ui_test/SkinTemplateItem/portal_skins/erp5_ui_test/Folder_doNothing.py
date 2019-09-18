from Products.ERP5Type.Log import log

log("Folder method received dialog_id, form_id, uids and {!s}".format(kwargs.keys()))

message = "First submission."

if kwargs.get("update_method", ""):
  return context.Base_renderForm(dialog_id, message="Updated. " + message)

if donothing_confirmation == 0:
  # Here is an example of an adversary Script which hijacks `keep_items`
  # It should take keep_items from parameters, update it and pass it
  # through. But no programmer will ever comply therefor we are ready!
  return context.Base_renderForm(dialog_id,
                                 message="Submit again to confirm. " + message,
                                 level='warning',
                                 keep_items={'donothing_confirmation': 1})

return context.Base_redirect(form_id, keep_items={"portal_status_message": message})
