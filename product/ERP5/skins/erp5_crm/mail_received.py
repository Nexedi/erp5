## Script (Python) "mail_received"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=theMail
##title=
##
import string

mail_message = None

try:

  id = container.strip_punctuation(theMail['headers']['message-id'])
  context.event.invokeFactory(type_name='Mail Message',
                          id=id,attachments=theMail['attachments'])

  mail_message = context.event.restrictedTraverse(id)
  subject=str(string.join(theMail['headers'].get('subject')))

  #subject = 'toto'

  kw={'title':theMail['headers'].get('subject'),
      #'subject':subject,
      'date':theMail['headers'].get('date'),
      'to':theMail['headers'].get('to'),
      'sender':theMail['headers'].get('from'),
      'reply_to':theMail['headers'].get('replyto'),
      'body':theMail['body'],
      'header':theMail['headers'],
      'other_info':theMail['localpart'],
  #    'attachment':theMail['attachments']
  }

  mail_message.edit(**kw)

  # We should now try to guess the user who sent it
  # Guess the mail address:
  mail_from = theMail['headers'].get('from')
  at_place = mail_from.find('@')
  mail_address = None
  if at_place != -1:
    begin = max(mail_from.rfind('<',0,at_place),mail_from.rfind(' ',0,at_place))
    end = min(mail_from.rfind('>',at_place),mail_from.rfind(' ',at_place),len(mail_from))
    mail_address = mail_from[begin+1:end]
  # find the person with this mail
  if mail_address is not None:
    kw = {'portal_type':'Email',
          'query':"SearchableText LIKE '%%%s%%'" % mail_address }
    result = context.portal_catalog.searchResults(**kw)
    for object in result:
      object = object.getObject()
      parent = object.aq_parent
      if parent.getPortalType() == 'Person':
        mail_message.setSourceValue(parent)
        mail_message.setSubordinationValue(parent.getSubordinationValue())
      if parent.getPortalType() == 'Organisation':
        mail_message.setSubordinationValue(parent)
      break

  # We should look if there's already a sale opportunity
  # or a support wich can corresponds to this email
  subject = mail_message.getTitle()
  if subject != '' and subject is not None:
    if subject.find('Re: ')==0:
      subject = subject[len('Re: '):]
    kw = {'portal_type':'Sale Opportunity',
          'query':"SearchableText LIKE '%%%s%%'" % subject }
    result = context.portal_catalog.searchResults(**kw)
    for object in result:
      object = object.getObject()
      # Check if this sale opportunity corresponds to this client
      # If so, then we can assign this mail to the sale opportunity
      if mail_message.getSourceValue() in object.getClientValueList():
        mail_message.setFollowUpValue(object)
        mail_message.assign()


except:
  try:
    if mail_message is not None and hasattr(edit):
      mail_message.edit(title='Bad mail message received')
  except:
    pass

# the return of None indicates a success
# The return of anything else assumes that you are returning an error message
# and most MTA's will bounce that error message back to the mail sender
return None
