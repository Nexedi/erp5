from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery

portal_catalog = context.getPortalObject().portal_catalog
if kw.get('path'):
  assert 'uid' not in kw
  kw['uid'] = [
    b.uid for b in portal_catalog(portal_type=kw['portal_type'], path=kw.pop('path'))
  ] or [-1]

kw['query'] = ComplexQuery(
  Query(portal_type='Simulation Movement', explanation_portal_type='Returned Sale Order'),
  ComplexQuery(
    Query(parent_specialise_portal_type=['Order Rule', 'Delivery Rule', 'Delivery Root Simulation Rule'],
          simulation_state='confirmed'),
    Query(parent_specialise_portal_type='Delivery Simulation Rule',
          grand_parent_simulation_state='confirmed'),
    logical_operator='or'),
  logical_operator='and')

kw['delivery_uid'] = None
kw['left_join_list'] = ['delivery_uid']
kw['select_dict'] = dict(delivery_uid=None)
kw['group_by'] = ('uid',)

kw['src__'] = src__
return portal_catalog(**kw)
