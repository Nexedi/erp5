kw['parent_specialise_portal_type'] = ['Open Order Rule']
kw['explanation_portal_type'] = 'Open Sale Order'
kw['portal_type'] = 'Simulation Movement'

kw['delivery_uid'] = None
kw['left_join_list'] = ['delivery_uid']
kw['select_dict'] = dict(delivery_uid=None)
kw['group_by'] = ('uid',)

return context.portal_catalog(**kw)
