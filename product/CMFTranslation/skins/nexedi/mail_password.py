REQUEST=context.REQUEST
try:
  return context.portal_registration.mailPassword(REQUEST['userid'], REQUEST)
except 'NotFound', error:
   message = error
except 'ValueError', error:
   message = error

redirect_url = '%s/mail_password_form?portal_status_message=%s' % ( context.absolute_url()
                            ,  message
                            )

REQUEST.RESPONSE.redirect( redirect_url )