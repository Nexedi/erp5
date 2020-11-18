message = context.updateRoleMappings(context.REQUEST)
return context.Base_redirect(form_id, keep_items={'portal_status_message': message})
