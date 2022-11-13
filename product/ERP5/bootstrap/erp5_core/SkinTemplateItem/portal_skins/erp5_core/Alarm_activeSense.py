from Products.ERP5Type.Message import translateString
context.activeSense()
return context.Base_redirect(
  form_id,
  keep_items={'portal_status_message': translateString('Active Sense Called.')})
