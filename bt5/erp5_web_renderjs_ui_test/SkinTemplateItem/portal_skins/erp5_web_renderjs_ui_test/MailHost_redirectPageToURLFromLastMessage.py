import re
last_message_text = context.getMessageList()[-1][2]
try:
  url = re.findall(r"http.*", last_message_text)[0]
except IndexError:
  raise RuntimeError("URL not found in the email")
else:
  return container.REQUEST.RESPONSE.redirect(url)
