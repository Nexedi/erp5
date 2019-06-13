context.setTextContent(context.getTextContent() + "\n" + field_your_reply)
context.respond()
return context.Base_redirect('view', keep_items=dict(portal_status_message="Responded"))
