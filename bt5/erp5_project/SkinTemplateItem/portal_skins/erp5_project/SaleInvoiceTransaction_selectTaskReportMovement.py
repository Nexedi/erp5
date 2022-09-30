kw['parent_specialise_portal_type'] = 'Invoice Simulation Rule'
kw['explanation_portal_type'] = 'Task', 'Task Report'
kw['portal_type'] = 'Simulation Movement'
kw['grand_parent_simulation_state'] = 'started', 'stopped', 'delivered'

kw['delivery_uid'] = None
kw['left_join_list'] = ['delivery_uid']
kw['select_dict'] = dict(delivery_uid=None)
kw['group_by'] = ('uid',)

kw['src__'] = src__
return context.portal_catalog(**kw)
