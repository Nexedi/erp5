kw['parent_specialise_reference'] = 'default_bank_reconciliation_rule'
kw['delivery_uid'] = None
kw['left_join_list'] = ['delivery_uid']
kw['select_dict'] = dict(delivery_uid=None)
kw['group_by'] = ('uid',)

kw['src__'] = src__

return context.portal_catalog(**kw)
