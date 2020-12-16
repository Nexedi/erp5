"""Find and returns Person object for current logged in user.
Returns None if no corresponding person, for example when not using ERP5Security.ERP5UserManager.
"""
from erp5.component.module.Log import log
if user_name is None:
  log('DEPRECATED: call context.getPortalObject().portal_membership.getAuthenticatedMember().getUserValue()')
  return context.getPortalObject().portal_membership.getAuthenticatedMember().getUserValue()
log('DEPRECATED: call context.Base_getUserValueByUserId(user_name)')
return context.Base_getUserValueByUserId(user_name)
