# This script has 'Anonymous' proxy role to check 'View' permission for Anonymous.
if 'format' in container.REQUEST:
  from zExceptions import Unauthorized
  portal = context.getPortalObject()
  try:
    return portal.portal_membership.checkPermission(
      'View', context)
  except Unauthorized:
    pass
return False
