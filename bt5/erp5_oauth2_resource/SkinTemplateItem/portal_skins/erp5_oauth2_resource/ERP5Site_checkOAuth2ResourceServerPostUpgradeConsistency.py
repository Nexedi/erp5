error_list = []
# XXX: duplicates a value from product/ERP5/ERP5Site.py
# It would be better to check plugin class, and not just its id.
plugin_id = 'erp5_oauth2_resource'
user_folder = context.getPortalObject().acl_users
if plugin_id not in user_folder:
  # XXX: does not check plugin personalities registration, but these are
  # automaticaly done on plugin creation, so unregistering them should be
  # a conscious admin action, that should likely be respected.
  error_list.append('PAS plugin %r does not exist' % (plugin_id, ))
  if fixit:
    user_folder.manage_addProduct['ERP5Security'].addERP5OAuth2ResourceServerPlugin(
      id=plugin_id,
    )
return error_list
