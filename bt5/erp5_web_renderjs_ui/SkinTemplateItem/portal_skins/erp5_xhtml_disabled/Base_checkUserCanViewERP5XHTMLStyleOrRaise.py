from zExceptions import Forbidden
from AccessControl import getSecurityManager

preference_tool = context.getPortalObject().portal_preferences
if preference_tool.isPreferredHtmlStyleDisabled():
  u = getSecurityManager().getUser()
  user_id = u.getId()

  if user_id:
    if user_id not in preference_tool.getPreferredHtmlStyleAllowedUserIdList():
      raise Forbidden('xhtml_style is disabled. Please use ERP5JS')
  else:
    # user should be able to login
    if not context.REQUEST['PATH_INFO'].endswith('login_form'):
      raise Forbidden('xhtml_style is disabled. Please use ERP5JS')
