from AccessControl import getSecurityManager
return getSecurityManager().getUser().has_permission('Manage portal', context)
