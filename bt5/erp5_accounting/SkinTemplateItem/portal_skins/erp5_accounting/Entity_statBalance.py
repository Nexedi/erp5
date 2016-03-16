"""Total balance of all accounting transactions having this
entity as a mirror section.
"""
kw['mirror_section_uid']=context.getUid()
kw['node_category_strict_membership'] = ['account_type/asset/receivable',
                                         'account_type/liability/payable']
return context.Node_statAccountingBalance(**kw)
