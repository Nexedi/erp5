kw['parent_specialise_portal_type'] = 'Invoice Simulation Rule'
kw['explanation_portal_type'] = 'Sale Order', 'Sale Packing List', 'Returned Sale Packing List', 'Returned Sale Order'
kw['portal_type'] = 'Simulation Movement'
kw['grand_parent_simulation_state'] = 'started', 'stopped', 'delivered'

kw['delivery_uid'] = None
kw['left_join_list'] = ['delivery_uid']
kw['select_dict'] = dict(delivery_uid=None)

# We assume that all simulation movements without a delivery are in planned or auto planned state.
# By passing this, catalog should use an index on portal_type + simulation state.
# XXX actually we do not even pass auto_planned to have only 1 value, because we just do not use
# auto_planned state in this project.
kw['simulation_state'] = ('planned', )

return context.portal_catalog(**kw)
