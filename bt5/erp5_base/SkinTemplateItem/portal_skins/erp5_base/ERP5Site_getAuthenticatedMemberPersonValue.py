"""Find and returns Person object for current logged in user.
Returns None if no corresponding person, for example when not using ERP5Security.ERP5UserManager.
"""
portal = context.getPortalObject()
if user_name is None:
  user_name = portal.portal_membership.getAuthenticatedMember()

from Products.ERP5Security.ERP5UserManager import getUserByLogin
found_user_list = getUserByLogin(portal, str(user_name))
if len(found_user_list) == 1:
  return found_user_list[0]
