from zExceptions import Forbidden
from AccessControl import getSecurityManager

preference_tool = context.getPortalObject().portal_preferences
if preference_tool.isPreferredHtmlStyleDisabled():
  u = getSecurityManager().getUser()
  user_id = u.getId()

  if user_id not in preference_tool.getPreferredHtmlStyleAllowedUserIdList():
    raise Forbidden('xhtml_style is disabled. Please use ERP5JS')
