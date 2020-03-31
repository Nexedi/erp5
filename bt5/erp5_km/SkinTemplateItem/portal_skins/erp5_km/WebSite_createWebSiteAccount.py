"""
  Create basic KM account using ERP5 credentials system.
"""
translateString = context.Base_translateString
website = context.getWebSiteValue()

# Call Base_edit
result, result_type = context.Base_edit(form_id, silent_mode=1, field_prefix='your_')

# Return if not appropriate
if result_type != 'edit':
  return result
kw, _ = result

# XXX: hard coded due to erp5_credentials requirement
kw['role_list'] = ['internal']
kw.pop('password_confirm', None)
default_email_text = reference = kw.pop('default_email_text')
context.ERP5Site_newCredentialRequest(reference=reference, \
                                      default_email_text=default_email_text, **kw)

msg = translateString("Your account was successfully created. You will be notified by email how to proceed.")
return website.Base_redirect(form_id, keep_items=dict(portal_status_message=msg,
                             editable_mode=0))
