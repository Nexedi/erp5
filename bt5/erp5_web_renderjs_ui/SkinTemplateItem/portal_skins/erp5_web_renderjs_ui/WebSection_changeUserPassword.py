"""
  The method changeUserPassword ignore came_from if you are in the Web Site context.
"""
REQUEST = context.REQUEST
response = REQUEST.RESPONSE
portal = context.getPortalObject()
translateString = portal.Base_translateString

password_confirm, password = REQUEST['password_confirm'], REQUEST['password']
new_url = "".join([x for x in REQUEST["HTTP_REFERER"].split("&")
  if "portal_status_message" not in x])

if password_confirm != password:
  return response.redirect(
    "%s&portal_status_message=%s" % (
      new_url,
      translateString("Passwords do not match."))
  )

password_key = REQUEST['password_key']

assert password_key
validation_message_list = portal.portal_password.analyzePassword(password, password_key)

if validation_message_list:
  message = ' '.join([x for x in validation_message_list])
  return response.redirect(
    "%s&portal_status_message=%s" % (
      new_url,
      message)
  )

return response.redirect(portal.portal_password.changeUserPassword(password=password,
                                                     password_confirmation=password_confirm,
                                                     password_key=password_key,
                                                     user_login=REQUEST.get('user_login', None),
                                                     REQUEST=REQUEST))
