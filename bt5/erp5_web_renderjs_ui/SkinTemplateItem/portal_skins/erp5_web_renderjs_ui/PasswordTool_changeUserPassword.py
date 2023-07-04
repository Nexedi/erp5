"""
  The method changeUserPassword ignore came_from if you are in the Web Site context.
"""
REQUEST = context.REQUEST
next_url = context.portal_password.changeUserPassword(password=REQUEST['password'],
                                                      password_confirm=REQUEST['password_confirm'],
                                                      password_key=REQUEST['password_key'],
                                                      user_login=REQUEST.get('user_login', None),
                                                      REQUEST=REQUEST)
root_url = "%s/" % context.getWebSiteValue().absolute_url()
return REQUEST.RESPONSE.redirect("%s&came_from=%s" % (next_url, root_url))
