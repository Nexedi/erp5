kw['portal_type'] = 'Simulation Movement'
kw['delivery_uid'] = None
kw['left_join_list'] = ['delivery_uid']
kw['select_dict'] = dict(delivery_uid=None)
kw['group_by'] = ('uid',)
kw['grand_parent_simulation_state'] = 'started', 'stopped', 'delivered'

result = context.portal_catalog(**kw)
context.log("%r => %r" % (kw, [brain.getObject() for brain in result]))

return result
