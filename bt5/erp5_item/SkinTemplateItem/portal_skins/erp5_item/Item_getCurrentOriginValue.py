portal = context.getPortalObject()

last_affectation_list = context.Item_getAffectationList(**kw)
if not last_affectation_list:
  return None

if last_affectation_list[-1].delivery_uid is not None:
  site = portal.portal_catalog.getObject(last_affectation_list[-1].delivery_uid)
  return site
