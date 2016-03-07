"""Total debit of all accounting transactions having this
entity as a mirror section
"""
kw['mirror_section_uid'] = context.getUid()
kw['omit_asset_decrease'] = 1
kw['node_category_strict_membership'] = ['account_type/asset/receivable',
                                         'account_type/liability/payable']
kw.update(kw['selection'].getParams())

return context.Node_statAccountingBalance(**kw)
