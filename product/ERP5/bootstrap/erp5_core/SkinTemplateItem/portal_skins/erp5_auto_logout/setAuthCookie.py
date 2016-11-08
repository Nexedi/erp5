from base64 import standard_b64encode, standard_b64decode
if cookie_value is not None and login is None:
  from urllib import unquote
  login, password = unquote(cookie_value).decode('base64').split(':', 1)
 
portal = context.getPortalObject()
portal.acl_users.updateCredentials(context.REQUEST, resp, login, password)
