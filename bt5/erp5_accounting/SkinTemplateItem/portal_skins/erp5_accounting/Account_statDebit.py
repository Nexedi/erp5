"""Total debit of all accounting transactions having this
account as a node
"""
kw['node_uid'] = context.getUid()
kw['omit_asset_decrease'] = 1
kw.update(kw['selection'].getParams())

return context.Node_statAccountingBalance(**kw)
