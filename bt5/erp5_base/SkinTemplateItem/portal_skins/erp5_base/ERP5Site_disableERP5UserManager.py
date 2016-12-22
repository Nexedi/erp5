portal = context.getPortalObject()
acl_users = portal.acl_users
plugin_id = 'erp5_users'
getattr(acl_users, plugin_id).manage_activateInterfaces([])
