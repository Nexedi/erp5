translateString = context.Base_translateString

# Call Base_edit
result, result_type = context.Base_edit('Person_viewAsWeb', silent_mode=1, field_prefix='my_')

# Return if not appropriate
if result_type != 'edit':
  return result # XXX add support for editable in this call

# Update data

kw, _ = result
context.edit(**kw)

login_come_from_url = context.REQUEST.get("field_your_login_come_from_url")
edit_portal_status_message = context.REQUEST.get("field_your_edit_portal_status_message",
                                      translateString("Your personal informations are now updated."))

if login_come_from_url is not None:
  from ZTUtils import make_query
  query = make_query({'portal_status_message': edit_portal_status_message})
  return context.REQUEST.RESPONSE.redirect(login_come_from_url + "?%s" % query )

return context.Base_redirect(context.REQUEST.get("form_id", ""), \
                          keep_items={'portal_status_message': edit_portal_status_message})
