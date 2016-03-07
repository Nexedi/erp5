"""Total balance of all accounting transactions having this
account as node
"""
kw['node_uid'] = context.getUid()
return context.Node_statAccountingBalance(**kw)
