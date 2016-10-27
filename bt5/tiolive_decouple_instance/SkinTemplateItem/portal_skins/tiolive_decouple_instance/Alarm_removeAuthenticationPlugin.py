"""
  Script removes the nexedi_authentication plugin.
"""
plugin_id = "nexedi_authentication"
user_folder = context.getPortalObject().acl_users
user_folder.manage_delObjects('nexedi_authentication')

erp5_login_users_plugin = getattr(user_folder, "erp5_login_users")
erp5_login_users_plugin.manage_activateInterfaces(interfaces=['IAuthenticationPlugin', 'IUserEnumerationPlugin'])

return True
