from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery

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
return context.portal_catalog(**kw)
