"""Returns Accounting Transactions where this bank account is payment.
"""
kw['payment_uid'] = context.getUid()
kw['node_category'] = 'account_type/asset/cash/bank'
transaction_list = context.Node_getAccountingTransactionList(**kw)

# As we are showing quantities and not asset prices, we use the precision
# from this bank account currency
if context.getPriceCurrency():
  container.REQUEST.set('precision',
    context.getQuantityPrecisionFromResource(context.getPriceCurrency()))

return transaction_list
