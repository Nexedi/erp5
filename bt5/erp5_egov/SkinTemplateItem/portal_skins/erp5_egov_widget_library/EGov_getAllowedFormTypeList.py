portal_types = context.getPortalObject().portal_types
portal_type_list = portal_types.searchFolder(portal_type='EGov Type', validation_state = 'validated')

portal_type_anon_list = ()
portal_type_auth_list = ()
for portal_type in portal_type_list:
  if portal_type.getStepAuthentication():
    portal_type_auth_list += (portal_type.getTitle(),)
  else:
      portal_type_anon_list += (portal_type.getTitle(),)
if context.portal_membership.isAnonymousUser():
  return portal_type_anon_list
return portal_type_auth_list
