"""Returns true if the reconciled balance at the begin date of this bank reconciliation
matches the previous account balance.
"""
precision = 3
if context.getSourcePayment():
  precision = context.getQuantityPrecisionFromResource(
        context.getSourcePaymentValue().getPriceCurrency())


return round(context.getQuantityRangeMin(), precision) \
  == round(context.BankReconciliation_getReconciledAccountBalance(
                 at_date=context.getStartDate().latestTime()), precision)
