"""Returns Simulation Movements for invoice

Simulation Movements can come from normal Invoice Transaction Rule
and same rule which is children of Trade Model Rule """

# search for normal movements
kw['parent_specialise_reference'] = ['default_invoice_transaction_rule']
kw['grand_grand_parent_specialise_reference'] = [
             'default_invoicing_rule', 'default_invoice_rule', 'default_tax_rule']
if context.Invoice_isAdvanced():
  kw['explanation_portal_type']       = ['%s Order' % trade_type,
                                         '%s Invoice' % trade_type,
                                         '%s Packing List' % trade_type,
                                         'Returned %s Packing List' % trade_type]
else:
  kw['explanation_portal_type']       = ['%s Order' % trade_type,
                                         '%s Invoice Transaction' % trade_type,
                                         '%s Packing List' % trade_type,
                                         'Returned %s Packing List' % trade_type]
kw['portal_type']                   = 'Simulation Movement'

kw['delivery_uid'] = None
kw['left_join_list'] = ['delivery_uid']
kw['select_dict'] = dict(delivery_uid=None)
kw['group_by'] = ('uid',)

search_kw = kw.copy()
search_kw['grand_parent_simulation_state'] = ['started']

movement_list = list(context.portal_catalog(**search_kw))

# update query to search for movements which are children of Trade Model Rule
kw['grand_grand_parent_specialise_reference'] = 'default_trade_model_rule'
kw['grand_grand_grand_parent_simulation_state'] = ['started']

movement_list += list(context.portal_catalog(**kw))

# Simulation movement's state maybe not yet updated, make sure it's the right one
return [x for x in movement_list if x.getParentValue().getParentValue().getSimulationState() == 'started']
