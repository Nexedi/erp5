def _checkPermission(folder):
  msg=''
  if hasattr(folder, 'objectValues'):
    for child in folder.objectValues():
      msg += _checkPermission(child)
  if hasattr(folder, 'valid_roles'):
    valid_role_list = folder.valid_roles()
    manager_index = list(valid_role_list).index('Manager')
    permission_list = folder.permission_settings()
    for permission in permission_list:
      if permission['acquire'] == '':
        for role in permission['roles']:
          name = role['name']
          pos = name.find('r')
          index = int(name[pos+1:])
          if manager_index == index:
            if role['checked'] == '':
              msg += '%s: %s does not contain Manager\n' % (folder.getUrl(), permission['name'])
            break
  return msg

def ERP5Site_checkAllPermissions(self):
  portal = self.portal_url.getPortalObject()
  return _checkPermission(portal)
