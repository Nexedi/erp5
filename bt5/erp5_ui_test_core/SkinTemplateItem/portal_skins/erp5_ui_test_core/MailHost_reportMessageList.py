"""
  Get the Message List from DummyMailHost.

  This is used by functional tests to get all
  emails sent by the instance. This will prevent
  the instance spam mailing lists during the
  Functional Tests.
"""
if getattr(context.MailHost, "getMessageList", None) is None:
  return "ERROR: MailHost is not a DummyMailHost"

message_list = context.MailHost.getMessageList()
for mail in message_list:
  for part in mail:
    print(part)
  print("="*79)
  print("")

print("Total messages: %s" %len(message_list))

# If messages "looks like html", zope will set content type to text/html,
# and the assertTextPresent from selenium will be applied after the emails
# are interpreted as html.
# For example, the email  "Name <email@example.com>" would be interpreted as
# an html entity and we cannot use assertTextPresent on it.
# To prevent that, we force content type to text.
container.REQUEST.RESPONSE.setHeader('Content-Type', 'text/plain;charset=utf-8')

return printed
