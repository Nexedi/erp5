## Script (Python) "Coramy_sendMailToUser"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=user_name='rc',mMsg='Message par défaut', mSubj='Sujet par défaut',**kw
##title=
##
try:
   mailhost=getattr(context, context.portal_url.superValues('Mail Host')[0].id)
except:
   raise AttributeError, "Cannot find a Mail Host object"

mFrom = context.portal_properties.email_from_name+' <'+context.portal_properties.email_from_address+'>'

# Only for doing test
if user_name == 'rc':
  user_name = 'Romain_Courteaud'

mTo = user_name + '@coramy.com'

try:
    # send mail to user
    mailhost.send(mMsg,mTo,mFrom,mSubj)
    # send mail to admin
    mailhost.send(mMsg,mFrom,mFrom,mSubj)

except:
    mNewMsg = 'Sujet ' + mSubj + '\n'
    mNewMsg += 'Destinataire ' + mTo + '\n'
    mNewMsg += 'Message ' + mMsg + '\n'
    
    mailhost.send(mNewMsg,mFrom,mFrom,"ERP5:Coramy_sendMailToUser:Erreur")
