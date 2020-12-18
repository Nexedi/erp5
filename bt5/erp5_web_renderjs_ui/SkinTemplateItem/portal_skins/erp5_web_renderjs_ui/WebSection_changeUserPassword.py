"""
  The method changeUserPassword ignore came_from if you are in the Web Site context.
"""
REQUEST = context.REQUEST
response = REQUEST.RESPONSE
portal = context.getPortalObject()

password_confirm, password = REQUEST['password_confirm'], REQUEST['password']
new_url = "".join([x for x in REQUEST["HTTP_REFERER"].split("&")
  if "portal_status_message" not in x])

if password_confirm != password:
  return response.redirect(
    "%s&portal_status_message=%s" % (
      new_url,
      "New password does not match confirmation")
  )

password_key = REQUEST['password_key']

assert password_key
validation_message_list = portal.portal_password.analyzePassword(password, password_key)

if validation_message_list:
  message = u' '.join([str(x) for x in validation_message_list])
  return response.redirect(
    "%s&portal_status_message=%s" % (
      new_url,
      message)
  )

next_url = portal.portal_password.changeUserPassword(password=password,
                                                     password_confirmation=password_confirm,
                                                     password_key=password_key,
                                                     user_login=REQUEST.get('user_login', None),
                                                     REQUEST=REQUEST)
root_url = "%s/" % context.getWebSiteValue().absolute_url()
return response.redirect("%s&came_from=%s" % (next_url, root_url))
