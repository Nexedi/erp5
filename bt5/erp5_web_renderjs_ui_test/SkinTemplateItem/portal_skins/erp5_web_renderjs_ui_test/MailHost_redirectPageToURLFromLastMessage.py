import re
last_message_text = context.getMessageList()[-1][2]
return container.REQUEST.RESPONSE.redirect(re.findall(r"http.*", last_message_text)[0])
