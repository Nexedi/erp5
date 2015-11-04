obj = state_change['object']
for plugin in obj.getPortalObject().acl_users.objectValues():
  if getattr(plugin, 'getLoginPortalType', lambda: None)() == obj.getPortalType():
    plugin.unregisterLogin(obj)
