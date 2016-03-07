"""
  The customer must be notified about the decouple.
"""
mto = "tiolive-backup@tiolive.com"
mfrom = context.getPortalObject().email_from_address
subject = 'Your TioLive Instance has been decoupled from TioLive Master.'
message =  ["""
 Your TioLive Instance have been decoupled from TioLive Master.
 It means that all the user information has been moved to your instance and from now the user authentication will be done locally.
 The user authentication will be much faster now.
 
 TioLive Instance Id: %s

 List of users which have been moved to your instance:\n""" % context.ERP5Site_getExpressInstanceUid()]

for person in person_list:
  message.append(" %s\n" % person)

context.MailHost.send(''.join(message), mto, mfrom, subject)
