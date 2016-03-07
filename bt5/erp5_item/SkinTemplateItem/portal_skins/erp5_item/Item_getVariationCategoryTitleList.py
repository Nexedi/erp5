last_affectation_list = context.Item_getAffectationList(**kw)
if len(last_affectation_list):
  last_affectation = last_affectation_list[0]
  if last_affectation.delivery_uid is not None:
    portal = context.getPortalObject()
    movement = portal.portal_catalog.getObject(last_affectation.delivery_uid)
    variation_list = [x[0] for x in movement.getVariationCategoryItemList()]
    variation = ','.join(variation_list)
    return variation

return []
