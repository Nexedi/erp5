from zExceptions import Unauthorized

if REQUEST is not None:
  raise Unauthorized

portal_catalog = context.getPortalObject().portal_catalog

login = portal_catalog.getResultValue(
  portal_type="Google Login",
  reference=login,
  validation_state="validated")

if login is not None:
  return login.getParentValue().getRelativeUrl()
