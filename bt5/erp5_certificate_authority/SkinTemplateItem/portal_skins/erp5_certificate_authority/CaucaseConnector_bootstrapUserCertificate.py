if context.getUrlString() is None:
  raise ValueError('Please set Caucase Url before bootstrap!')

if not context.hasUserCertificateRequestReference():
  edit_kw={}
  
  if company_name:
    edit_kw['company_name'] = company_name
  
  if country_name:
    edit_kw['country_name'] = country_name
  
  if email_address:
    edit_kw['email_address'] = email_address
  
  if locality_name:
    edit_kw['locality_name'] = locality_name
  
  if state_or_province_name:
    edit_kw['state_or_province_name'] = state_or_province_name
  
  if edit_kw:
    context.edit(**edit_kw)

context.bootstrapCaucaseConfiguration()

if context.hasUserCertificateRequestReference() and not context.hasUserCertificate():
  message = context.Base_translateString("User certificate requested, but it is not ready, please reinvoke this action to update.")
else:
  message = context.Base_translateString("Data Updated.")
return context.Base_redirect('view', keep_items={'portal_status_message': message})
