portal = context.getPortalObject()
acl_users = portal.acl_users
plugin_id = 'erp5_users'
error_list = []
if plugin_id in acl_users.plugins.getAllPlugins(plugin_type='IAuthenticationPlugin')['active']:
  error_list.append('ERP5 User Manager is still active as %s/%s' % (acl_users.getPath(), plugin_id))
  if fixit:
    tag = 'person_login_migration'
    portal.portal_catalog.activate(tag=tag, activity='SQLQueue').searchAndActivate(
      portal_type='Person',
      activate_kw={'tag': tag, 'priority': 6},
      method_id='Person_migrateToERP5Login',
      method_kw={'tag': tag},
    )
    portal.portal_activities.activate(after_tag=tag).ERP5Site_disableERP5UserManager()
return error_list
