url = context.getPortalObject().absolute_url()
portal_object = context.getPortalObject()
acl_users = portal_object.acl_users
if not acl_users.getUserById('tiosafe_sync_user'):
  acl_users.zodb_users.manage_addUser(
      user_id='tiosafe_sync_user',
      login_name='tiosafe_sync_user',
      password='tiosafe_sync_user',
      confirm='tiosafe_sync_user',
  )
  acl_users.zodb_roles.manage_assignRoleToPrincipals(
      'Manager',
      ('tiosafe_sync_user',),
      RESPONSE=None)

for im in context.objectValues(portal_type="Integration Module"):
  sub = im.getDestinationSectionValue()
  pub = im.getSourceSectionValue()
  pub.edit(url_string=url)
  sub.edit(url_string=url, subscription_url_string=url, user_id='tiosafe_sync_user', password="tiosafe_sync_user")

message = context.Base_translateString("Synchronization update to url ${url}.", mapping=dict(url=url))
return context.Base_redirect(keep_items=dict(portal_status_message=message))
