portal = container.getPortalObject()
if not(id_value.endswith(portal.restrictedTraverse(REQUEST.object_path)\
                         .getIdAsReferenceSuffix())):
  return 0
return 1
