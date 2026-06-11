portal_catalog = context.getPortalObject().portal_catalog
if kw.get('path'):
  assert 'uid' not in kw
  kw['uid'] = [
    b.uid for b in portal_catalog(portal_type=kw['portal_type'], path=kw.pop('path'))
  ] or [-1]

kw['portal_type'] = 'Simulation Movement'
kw['explanation_portal_type'] = ['Sale Order', 'Sale Packing List']
kw['delivery_uid'] = None
kw['left_join_list'] = ['delivery_uid']
kw['select_dict'] = dict(delivery_uid=None)
kw['parent_specialise_portal_type'] = 'Loyalty Transaction Simulation Rule'
kw['grand_parent_simulation_state'] ='delivered'
return portal_catalog(**kw)
