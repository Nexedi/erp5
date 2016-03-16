"""Returns Accounting Transactions related to the project.
"""
kw['project_uid'] = context.getUid()
return context.Node_getAccountingTransactionList(**kw)
