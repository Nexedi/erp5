root = context.portal_url.getPortalObject()
acl_users = root.acl_users
acl_users.manage_exportObject(id='acl_users')
return "ok"

