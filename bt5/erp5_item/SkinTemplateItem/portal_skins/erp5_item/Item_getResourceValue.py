portal = context.getPortalObject()
last_affectation_list = context.Item_getAffectationList(**kw)

if last_affectation_list:
  last_affectation = last_affectation_list[0]
  if last_affectation.resource_uid is not None:
    resource_value = portal.portal_catalog.getObject(last_affectation.resource_uid)
    return resource_value

return None
