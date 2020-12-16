kw['portal_type'] = 'Simulation Movement'
kw['explanation_portal_type'] = ['Sale Order', 'Sale Packing List']
kw['delivery_uid'] = None
kw['left_join_list'] = ['delivery_uid']
kw['select_dict'] = dict(delivery_uid=None)
kw['parent_specialise_portal_type'] = 'Loyalty Transaction Simulation Rule'
kw['grand_parent_simulation_state'] ='delivered'
return context.portal_catalog(**kw)
