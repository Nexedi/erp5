from zExceptions import Forbidden
from AccessControl import getSecurityManager

preference_tool = context.getPortalObject().portal_preferences
if preference_tool.isPreferredHtmlStyleDisabled():
  u = getSecurityManager().getUser()
  user_id = u.getId()
  allowed_user_id_list = preference_tool.getPreferredHtmlStyleAllowedUserIdList()
  #user is not in allowed list or anonymous access when allowed list is empty
  if (user_id and user_id not in allowed_user_id_list) or (not user_id and not allowed_user_id_list):
    raise Forbidden('xhtml_style is disabled. Please use ERP5JS')
