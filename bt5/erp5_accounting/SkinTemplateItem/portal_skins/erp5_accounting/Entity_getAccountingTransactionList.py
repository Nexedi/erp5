"""Returns Accounting Transactions where this entity is mirror section.
"""
kw['mirror_section_uid'] = context.getUid()
kw['node_category_strict_membership'] = ['account_type/asset/receivable',
                                         'account_type/liability/payable']
return context.Node_getAccountingTransactionList(**kw)
