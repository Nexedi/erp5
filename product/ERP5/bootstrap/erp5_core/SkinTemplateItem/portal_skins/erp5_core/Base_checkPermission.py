# Check for a permission on an object specified by a given path
# for current user. Return true only if the user is allowed.

portal = context.getPortalObject()
ob = portal.restrictedTraverse(path, None)
if ob is not None:
  return portal.portal_membership.checkPermission(permission, ob)
return False
