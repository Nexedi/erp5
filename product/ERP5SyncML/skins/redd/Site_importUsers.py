root = context.portal_url.getPortalObject()
root.manage_delObjects('acl_users')
root.manage_importObject('acl_users.zexp',set_owner=0)
return "ok"
