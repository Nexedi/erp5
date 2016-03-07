"""Returns true if the reconciled balance matches the account balance.
"""
precision = 3
if context.getSourcePayment():
  precision = context.getQuantityPrecisionFromResource(
        context.getSourcePaymentValue().getPriceCurrency())

return round(context.getQuantityRangeMax(), precision) \
  == round(context.BankReconciliation_getReconciledAccountBalance(), precision)
