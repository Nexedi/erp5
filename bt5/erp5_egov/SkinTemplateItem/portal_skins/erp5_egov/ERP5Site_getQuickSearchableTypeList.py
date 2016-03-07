from AccessControl import getSecurityManager
user=getSecurityManager().getUser()

portal_types = context.getPortalObject().portal_types
validated_type_list = portal_types.searchFolder(portal_type='EGov Type', validation_state = 'validated')
access_permission= 'Access contents information'
view_permission = 'View'

portal_type_list = ()
for ptype_title in ['Person', 'Organisation']:
  default_module = context.getDefaultModule(ptype_title)
  if user.has_permission(access_permission,default_module) or user.has_permission(view_permission,default_module):
    portal_type_list += (ptype_title,)
  
for ptype in validated_type_list:
  default_module = context.getDefaultModule(ptype.getTitle())
  if user.has_permission(access_permission,default_module) or user.has_permission(view_permission,default_module):
    portal_type_list += (ptype.getTitle(),)

return portal_type_list
