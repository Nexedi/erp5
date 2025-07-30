context.appendData(append_file.read())
  
message = context.Base_translateString("Data Stream updated.")
return context.Base_redirect(
  'view', 
  keep_items=dict(portal_status_message=message)
)
