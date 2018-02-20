"""Stay there with a "Nothing" portal status message"""
kw.update(context.REQUEST.form)
return context.Base_redirect(kw['form_id'], keep_items={'portal_status_message': '"Nothing" action is done.'})
