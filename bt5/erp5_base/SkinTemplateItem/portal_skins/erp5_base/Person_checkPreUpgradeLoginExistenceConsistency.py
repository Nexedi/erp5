error_list = []
if context.hasReference() and \
    not len(context.objectValues(portal_type=context.getPortalObject().getPortalLoginTypeList())):
  error_list.append('%s has no Login type sub document.' % context.getRelativeUrl())
  if fixit:
    context.Person_migrateToLogin()
return error_list
