context.resetSubscriberList()

message = context.Base_translateString('Publication reset')
return context.Base_redirect(form_id, keep_items={'portal_status_message' : message}, **kw)
