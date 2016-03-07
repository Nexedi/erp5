"""Total credit of all accounting transactions having this
account as node
"""
kw['node_uid'] = context.getUid()
kw['omit_asset_increase'] = 1
kw.update(kw['selection'].getParams())

# here, or 0 is to prevent displaying "- 0"
return - context.Node_statAccountingBalance(**kw) or 0
