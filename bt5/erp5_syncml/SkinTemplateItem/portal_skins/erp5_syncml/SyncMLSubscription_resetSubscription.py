context.resetSignatureList()
context.resetAnchorList()

message = context.Base_translateString('Subscription reset')
return context.Base_redirect(form_id, keep_items={'portal_status_message' : message}, **kw)
