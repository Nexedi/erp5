"""Reset reconciliation after a copy & paste.

"""
context.setGroupingReference(None)
context.setGroupingDate(None)

context.setAggregate(None, portal_type='Bank Reconciliation')
context.setAggregate(None, portal_type='Payment Transaction Group')
