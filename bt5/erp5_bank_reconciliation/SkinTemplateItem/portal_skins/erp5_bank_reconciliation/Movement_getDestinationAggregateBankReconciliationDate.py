for bank_reconciliation in context.getAggregateValueList(portal_type='Bank Reconciliation'):
  if bank_reconciliation.getSourcePayment() == context.getDestinationPayment():
    return bank_reconciliation.getStopDate()
