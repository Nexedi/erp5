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
  subject = theMail['headers'].get('subject')
  attachments = theMail['attachments']
  if subject.find('PhoneCall:') >= 0 or subject.find('j2 Voice Message') >= 0:
    mail_message = context.event.newContent(portal_type='Phone Call', id=id)
  elif subject.find('Letter:') >= 0:
    mail_message = context.event.newContent(portal_type='Incoming Letter', id=id)
  elif subject.find('j2 Fax') >= 0 or subject.find('fax from') >= 0:
    mail_message = context.event.newContent(portal_type='Incoming Fax', id=id)
  else:
    mail_message = context.event.newContent(portal_type='Mail Message', id=id)

  subject=str(string.join(theMail['headers'].get('subject')))

  mail_message.edit(
                  title = theMail['headers'].get('subject'),
                  date = theMail['headers'].get('date'),
                  to = theMail['headers'].get('to'),
                  sender = theMail['headers'].get('from'),
                  reply_to = theMail['headers'].get('replyto'),
                  body = theMail['body'],
                  header = theMail['headers'],
                  other_info = theMail['localpart'],
                 )

  for key, attachment_data in attachments.items():
    try:
      #portal_type = context.content_type_registry.findTypeName(key, '//', attachment_data)
      portal_type = 'File'
      new_file = mail_message.newContent(portal_type = portal_type , id=key.replace('/','_'), file=attachment_data)  
    except:
      mail_message.setDescription('Error in creating attachments')
     

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
        organisation = parent.getSubordinationValue()
        if organisation is None:
          mail_message.setSourceValue(parent)
        else:
          mail_message.setSourceValueList([parent, organisation])
      elif parent.getPortalType() == 'Organisation':
        mail_message.setSourceValue(parent)
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
