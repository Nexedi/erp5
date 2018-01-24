kw['parent_specialise_reference'] = ['default_inventory_accounting_transaction_rule']
kw['grand_grand_parent_specialise_reference'] = ['default_delivering_rule', 'default_delivery_rule']
kw['explanation_portal_type'] = ['Sale Packing List', 'Purchase Packing List']
kw['portal_type'] = 'Simulation Movement'
kw['delivery_uid'] = None
kw['left_join_list'] = ['delivery_uid']
kw['select_dict'] = dict(delivery_uid=None)
kw['group_by'] = ('uid',)
kw['simulation_state'] = ['planned', 'auto_planned']

result = context.portal_catalog(**kw)
context.log("%r => %r" % (kw, [brain.getObject() for brain in result]))

return result
