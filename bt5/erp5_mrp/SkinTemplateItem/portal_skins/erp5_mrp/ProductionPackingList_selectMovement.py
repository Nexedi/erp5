portal_catalog = context.getPortalObject().portal_catalog
if kw.get('path'):
  assert 'uid' not in kw
  kw['uid'] = [
    b.uid for b in portal_catalog(portal_type=kw['portal_type'], path=kw.pop('path'))
  ] or [-1]

return portal_catalog(
  explanation_portal_type="Production Order",
  parent_specialise_portal_type="Delivery Simulation Rule",
  delivery_uid=None,
  left_join_list=("delivery_uid",),
  select_list=("delivery_uid",),
  group_by=("uid",),
  **kw)
