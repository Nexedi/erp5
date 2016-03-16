context.updateUrlRegistryTool()
message = context.Base_translateString('Url Registry Tool is currently rebuilding.')
context.Base_redirect(form_id, keep_items={'portal_status_message': message})
