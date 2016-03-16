"""Total credit of all accounting transactions having this
entity as a mirror section
"""

kw['mirror_section_uid'] = context.getUid()
kw['omit_asset_increase'] = 1
kw['node_category_strict_membership'] = ['account_type/asset/receivable',
                                         'account_type/liability/payable']
kw.update(kw['selection'].getParams())

# here, or 0 is to prevent displaying "- 0"
return - context.Node_statAccountingBalance(**kw) or 0
