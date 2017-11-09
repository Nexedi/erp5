"""Stay there with a "Nothing" portal status message"""
kw.update(context.REQUEST.form)
return context.ERP5Site_redirect(context.absolute_url(), keep_items={'portal_status_message': '"Nothing" action is done.'}, **kw)
