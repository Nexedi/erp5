acl_users = context.getPortalObject().acl_users
token_extraction_id = "erp5_access_token_plugin"

access_token_plugin_list = [
    plugin for plugin in acl_users.objectValues()
    if plugin.meta_type == 'ERP5 Access Token Extraction Plugin']

if len(access_token_plugin_list) > 1:
  return ["More than one plugin found: %s" % access_token_plugin_list]

error_list = []
if not access_token_plugin_list:
  error_list.append("erp5_access_token_plugin is missing")
  if fixit:
    dispacher = acl_users.manage_addProduct['ERP5Security']
    dispacher.addERP5AccessTokenExtractionPlugin(token_extraction_id)
    access_token_plugin_list = [getattr(acl_users, token_extraction_id)]

if access_token_plugin_list:
  access_token_plugin, = access_token_plugin_list
  # We only check that our plugin is enabled for IAuthenticationPlugin, this covers both
  # cases where plugin was not enabled at all or was enabled only for IExtractionPlugin
  IAuthenticationPlugin = [
    # Products.PluggableAuthService.interfaces.plugins.IAuthenticationPlugin cannot
    # be imported in restricted python but we can get it this way.
      x for x in acl_users.plugins.listPluginTypeInfo()
      if x['id'] == 'IAuthenticationPlugin'][0]['interface']
  if (access_token_plugin.getId()
        not in acl_users.plugins.listPluginIds(IAuthenticationPlugin)):
    error_list.append("erp5_access_token_plugin is not activated")
    if fixit:
      access_token_plugin.manage_activateInterfaces((
          'IExtractionPlugin',
          'IAuthenticationPlugin',))
return error_list
