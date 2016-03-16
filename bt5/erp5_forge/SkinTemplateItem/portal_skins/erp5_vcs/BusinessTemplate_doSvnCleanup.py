portal = context.getPortalObject()

context.getVcsTool().cleanup()

message = portal.Base_translateString('Subversion locks removed successfully.')
return context.Base_redirect(form_id, keep_items={'portal_status_message': message})
