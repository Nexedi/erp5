"""Find and returns Person object for current logged in user.
Returns None if no corresponding person, for example when not using ERP5Security.ERP5UserManager.
"""
portal = context.getPortalObject()
if user_name is None:
  return portal.portal_membership.getAuthenticatedMember().getUserValue()
user_path_set = {
  x['path']
  for x in portal.acl_users.searchUsers(exact_match=True, id=user_name)
  if 'path' in x
}
if len(user_path_set) == 1:
  user_path, = user_path_set
  return portal.restrictedTraverse(user_path)
