# This script has 'Anonymous' proxy role to check 'View' permission for Anonymous.
return 'format' in context.REQUEST and context.getPortalObject().portal_membership.checkPermission('View', context)
