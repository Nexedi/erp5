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


if theMail['headers'].get('to').find('server') >= 0:
  id = theMail['headers'].get('subject')
  msg = theMail['body']
  context.portal_synchronizations.PubSync(id,msg=msg)

elif theMail['headers'].get('to').find('client') >= 0:
  id = theMail['headers'].get('subject')
  msg = theMail['body']
  context.portal_synchronizations.SubSync(id,msg=msg)



# the return of None indicates a success
# The return of anything else assumes that you are returning an error message
# and most MTA's will bounce that error message back to the mail sender
return None
