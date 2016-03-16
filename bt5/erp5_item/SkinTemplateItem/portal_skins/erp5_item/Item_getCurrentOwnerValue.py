portal = context.getPortalObject()
last_affectation_list = context.Item_getAffectationList(**kw)

if last_affectation_list and last_affectation_list[0].section_uid:
  return portal.portal_catalog.getObject(last_affectation_list[0].section_uid)
