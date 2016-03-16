"""Total balance (in local currency) of all accounting transactions having this
bank account as payment node
"""
kw['payment_uid'] = context.getUid()
kw['asset_price'] = False
kw['node_category'] = 'account_type/asset/cash/bank'
return context.Node_statAccountingBalance(**kw)
