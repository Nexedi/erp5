email_reader = context.getParentValue()
title = context.getReplySubject()
text_content = context.getReplyBody()

id_group = "%s-sent" % email_reader.getRelativeUrl()
new_id = context.portal_ids.generateNewId(id_group=id_group)
new_id = "OUTBOX-%s" % new_id

# Prepare new message
new_message = email_reader.newContent(portal_type="Email Thread", id=new_id, title=title, text_content=text_content, text_format="text/plain")
new_message.setRecipient(context.getReplyTo())
# set In-Reply-To field
new_message.setDestinationReference(context.getSourceReference())

# Reply to old one
context.reply()

# And display
return new_message.Base_redirect()
