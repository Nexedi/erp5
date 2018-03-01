from zExceptions import Unauthorized

if REQUEST is not None:
  raise Unauthorized

login = context.ERP5Site_getFacebookLogin(login)

if login is None:
  return login

if len(login) > 1:
  raise ValueError("Duplicated User")

return login[0].getParentValue().getRelativeUrl()
