from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, NegatedQuery
portal = context.getPortalObject()

kw = {
  'section_uid': context.getSourceSection()
     and portal.Base_getSectionUidListForSectionCategory(
       context.getSourceSectionValue().getGroup(base=True)),
  'payment_uid': context.getSourcePaymentUid(),
  'node_category': 'account_type/asset/cash/bank',
  'simulation_state': ('stopped', 'delivered', ),
  'portal_type': portal.getPortalAccountingMovementTypeList(),
}

if not at_date and context.getStopDate():
  at_date = context.getStopDate().latestTime()

if at_date:
  kw['at_date'] = at_date
  kw['reconciliation_query'] = SimpleQuery(
      aggregate_bank_reconciliation_date=kw['at_date'], comparison_operator="<=")

if portal.REQUEST.get('reconciled_uid_list'):
  # This is to take into account lines we just reconciled.
  # We sum all reconciled lines execpt those we just reconciled + those we just
  # reconciled without applying the criterion on reconcilation
  kw['workaround_catalog_lag_query'] = NegatedQuery(SimpleQuery(uid=portal.REQUEST['reconciled_uid_list']))
  previously_reconciled = portal.portal_simulation.getInventory(**kw)

  kw.pop('workaround_catalog_lag_query')
  kw.pop('reconciliation_query')
  kw['uid'] = portal.REQUEST['reconciled_uid_list']
  return previously_reconciled + portal.portal_simulation.getInventory(**kw)

return context.portal_simulation.getInventory(**kw)
