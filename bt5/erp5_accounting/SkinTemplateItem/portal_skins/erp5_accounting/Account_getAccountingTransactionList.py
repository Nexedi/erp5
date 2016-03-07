"""Returns Accounting Transactions where this account is node.
"""
kw['node_uid'] = context.getUid()
return context.Node_getAccountingTransactionList(**kw)
