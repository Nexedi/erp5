"""Check that all transactions grouped together have a 0 balance.

In other words, check that all transactions grouped together really match.
"""

active_process = context.newActiveProcess().getRelativeUrl()

assert not fixit, NotImplemented

context.getPortalObject().portal_catalog.searchAndActivate(
   method_id='AccountingTransactionLine_checkGroupingReferenceIsValid',
   method_kw=dict(fixit=fixit, active_process=active_process),
   activate_kw=dict(tag=tag, priority=5),
   portal_type=context.getPortalAccountingMovementTypeList(),
   grouping_reference='%')
