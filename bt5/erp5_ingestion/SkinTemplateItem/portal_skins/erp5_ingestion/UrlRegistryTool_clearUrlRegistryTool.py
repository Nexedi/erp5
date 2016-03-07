context.clearUrlRegistryTool()
message = context.Base_translateString('Url Registry Tool cleared.')
context.Base_redirect(form_id, keep_items={'portal_status_message': message})
