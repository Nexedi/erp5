error_list = []
user_folder = context.getPortalObject().acl_users
for plugin_value in user_folder.objectValues():
  # Note: does not check plugin personalities registration, but these are
  # automaticly done on plugin creation, so unregistering them should be
  # a conscious admin action, that should likely be respected.
  # XXX: testing the type would be nicer than testing the meta_type attribute
  if getattr(plugin_value, 'meta_type', None) == 'ERP5 OAuth2 Resource Server Plugin':
    break
else:
  error_list.append('PAS plugin %r does not exist' % (plugin_id, ))
  if fixit:
    user_folder.manage_addProduct['ERP5Security'].addERP5OAuth2ResourceServerPlugin(
      id=plugin_id,
    )
return error_list
