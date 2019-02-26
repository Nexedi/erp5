acl_users = context.getPortalObject().acl_users
token_extraction_id = "erp5_access_token_plugin"

access_token_plugin_list = [
    plugin for plugin in acl_users.objectValues()
    if plugin.meta_type == 'ERP5 Access Token Extraction Plugin']

if len(access_token_plugin_list) > 1:
  return ["More than one plugin found: %s" % access_token_plugin_list]

error_list = []
if not access_token_plugin_list:
  # A dumb http extraction plugin is required as fallback if we use an access token
  # since https://github.com/Nexedi/erp5/commit/0bee523da0075c6efe3c06296dddd01d9dd5045a
  # we enable it automatically at site creation, but for compatibility with old instances
  # make sure it is created if needed
  if 'erp5_dumb_http_extraction' not in acl_users.objectIds():
    error_list.append("erp5_dumb_http_extraction is missing")
    if fixit:
      dispacher = acl_users.manage_addProduct['ERP5Security']
      dispacher.addERP5DumbHTTPExtractionPlugin('erp5_dumb_http_extraction')
      acl_users.erp5_dumb_http_extraction.manage_activateInterfaces(('IExtractionPlugin', ))

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
