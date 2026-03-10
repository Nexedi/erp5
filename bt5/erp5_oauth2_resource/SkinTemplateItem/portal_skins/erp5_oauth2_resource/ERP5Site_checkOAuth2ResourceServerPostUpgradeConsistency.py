user_folder = context.getPortalObject().acl_users
plugins = user_folder.plugins
plugin_id = 'erp5_oauth2_resource' # XXX hardcoded
ERP5Security = user_folder.manage_addProduct['ERP5Security']
# XXX: cannot import interface classes, but they are available through listPluginTypeInfo...
for info in plugins.listPluginTypeInfo():
  if info['id'] == 'IExtractionPlugin':
    IExtractionPlugin = info['interface']
    break
else:
  IExtractionPlugin = None # This should probably never happen, IExtractionPlugin is a very old plugin type

basic_auth_extractor_value = None
for plugin_value in user_folder.objectValues():
  # Note: does not check plugin personalities registration, but these are
  # automaticly done on plugin creation, so unregistering them should be
  # a conscious admin action, that should likely be respected.
  # XXX: testing the type would be nicer than testing the meta_type attribute
  meta_type = getattr(plugin_value, 'meta_type', None)
  if meta_type == 'ERP5 OAuth2 Resource Server Plugin':
    return []
  elif meta_type == 'ERP5 Dumb HTTP Extraction Plugin':
    basic_auth_extractor_value = plugin_value

error_list = [
  'PAS plugin %r does not exist' % (plugin_id, ),
]
if fixit:
  ERP5Security.addERP5OAuth2ResourceServerPlugin(id=plugin_id)
if IExtractionPlugin is not None:
  if not plugins.listPlugins(IExtractionPlugin):
    # When there is no pre-existing and enabled extraction plugin, enabling oauth will override PAS's default extraction plugin (DumbHTTPExtractor).
    # This could prevent the user from logging in, so add (if no instance of the ERP5 Dumb HTTP Extraction Plugin meta-type exists) and enable it.
    error_list.append('No pre-existing enabled IExtractionPlugin, will enable ERP5 Dumb HTTP Extraction Plugin')
    if fixit:
      if basic_auth_extractor_value is None:
        basic_auth_extractor_value = ERP5Security.addERP5DumbHTTPExtractionPlugin(
          id='erp5_dumb_http_extraction_plugin', # XXX: hardcoded
        )
      plugins.activatePlugin(
        IExtractionPlugin,
        basic_auth_extractor_value.getId(),
      )
return error_list
