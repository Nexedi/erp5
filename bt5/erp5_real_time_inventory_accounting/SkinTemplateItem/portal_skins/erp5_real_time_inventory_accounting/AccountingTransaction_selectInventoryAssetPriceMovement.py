kw['portal_type'] = 'Simulation Movement'
kw['delivery_uid'] = None
kw['left_join_list'] = ['delivery_uid']
kw['select_dict'] = dict(delivery_uid=None)
kw['group_by'] = ('uid',)
kw['grand_parent_simulation_state'] = 'started', 'stopped', 'delivered'

return context.portal_catalog(**kw)
