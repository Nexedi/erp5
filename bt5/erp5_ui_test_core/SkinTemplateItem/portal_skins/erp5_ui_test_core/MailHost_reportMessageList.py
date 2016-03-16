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
    print part
  print "="*79
  print ""  

print "Total messages: %s" %len(message_list)
return printed
