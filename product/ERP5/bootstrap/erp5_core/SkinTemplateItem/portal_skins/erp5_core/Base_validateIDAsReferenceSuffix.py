portal = container.getPortalObject()
if not(id_value.endswith(portal.restrictedTraverse(REQUEST.object_path)\
                         .getIdAsReferenceAffix())):
  return 0
return 1
