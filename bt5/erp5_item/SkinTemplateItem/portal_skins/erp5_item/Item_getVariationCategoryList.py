portal = context.getPortalObject()
last_affectation_list = context.Item_getAffectationList(**kw)

if len(last_affectation_list):
  last_affectation = last_affectation_list[0]
  if last_affectation.delivery_uid is not None:
    movement = portal.portal_catalog.getObject(last_affectation.delivery_uid)
    return movement.getVariationCategoryList()

return []
