"""
Sets initial title on transaction from title of aggregate Bank Reconciliation
Line if any.
"""

for accounting_line_value in context.objectValues():
  aggregate_value = accounting_line_value.getAggregateValue(portal_type="Bank Reconciliation Line")
  if aggregate_value is not None:
    context.setTitle(aggregate_value.getTitle())

context.PaymentTransaction_postGeneration(**kw)
