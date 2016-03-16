"""
  Script check if nexedi_authentication exists.
"""
plugin_id = "nexedi_authentication"
user_folder = context.getPortalObject().acl_users
acl_users_id_list = user_folder.objectIds()

if plugin_id in acl_users_id_list:
  return context.Alarm_decoupleInstance()

return False
