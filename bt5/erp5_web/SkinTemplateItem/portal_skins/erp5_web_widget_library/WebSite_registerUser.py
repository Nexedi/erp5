"""
  Script called by user registration form; checks if all required parameters
  are supplied, handles errors, calls WebSite_createUser to actually
  create Person.
  Will send email with password info.

  XXX - redirect, translation of dialogs
"""
from erp5.component.module.Log import log
req = context.REQUEST

# check if everything was filled
fields = ('email', 'email_repeated', 'group', 'function', 'site', 'first_name', 'last_name')
missing_string = ''
kwargs = {}
for f in fields:
  value = req.get('your_' + f)
  if not value:
    missing_string += '&missing:list=' + f
  else:
    kwargs[f] = value
returned_params = '&'.join([f+'='+kwargs[f] for f in kwargs])
log(returned_params)
if missing_string:
  params = returned_params + '&' + missing_string + '&portal_status_message=You did not fill all the required fields. See below to find out which fields still have to be filled.'
  log(params)
  return req.RESPONSE.redirect(context.absolute_url()+'?'+params)
if req.get('your_email') != req.get('your_email_repeated'):
  missing_string += '&missing:list=email&missing:list=email_repeated'
  params = returned_params + '&' + missing_string + '&portal_status_message=You entered two different email addresses. Please make sure to enter the same email address in the fields Email Address and Repeat Email Address.'
  return req.RESPONSE.redirect(context.absolute_url()+'?'+params)

# create a user
log(kwargs)
try:
  user = context.WebSite_createUser(**kwargs)
  log(user)
  msg = 'Thank you for registering. Your password will be sent to the email address that you provided once your account has been validated by the appropriate department.'
except Exception as e:
  msg = str(e)

return req.RESPONSE.redirect(context.absolute_url() + '?portal_status_message='+msg)
