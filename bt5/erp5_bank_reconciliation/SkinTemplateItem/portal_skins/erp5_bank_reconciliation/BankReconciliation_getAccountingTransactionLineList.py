from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, NegatedQuery
portal = context.getPortalObject()

kw = {
  'section_uid': context.getSourceSection()
     and portal.Base_getSectionUidListForSectionCategory(
       context.getSourceSectionValue().getGroup(base=True)),
  'payment_uid': context.getSourcePaymentUid(),
  'node_category': 'account_type/asset/cash/bank',
  'simulation_state': ('stopped', 'delivered', ),
  'portal_type': context.getPortalAccountingMovementTypeList(),
  'sort_on': (('date', 'ASC'), ('uid', 'ASC'))
}


if reconciliation_mode == "reconcile":
  if context.getStopDate():
    kw['at_date'] = context.getStopDate().latestTime()
  kw.update({
  'reconciliation_query': SimpleQuery(
      aggregate_bank_reconciliation_date=None),
  'left_join_list': ['aggregate_bank_reconciliation_date'],
  'implicit_join': False, })
else:
  assert reconciliation_mode == "unreconcile"
  kw['aggregate_bank_reconciliation_uid'] = context.getUid()

# Handle search params
if listbox_kw.get('Movement_getExplanationTitle'):
  kw['stock_explanation_title'] = listbox_kw['Movement_getExplanationTitle']
if listbox_kw.get('Movement_getExplanationReference'):
  kw['stock_explanation_reference'] = listbox_kw['Movement_getExplanationReference']
if listbox_kw.get('Movement_getExplanationTranslatedPortalType'):
  kw['stock_explanation_translated_portal_type'] = listbox_kw['Movement_getExplanationTranslatedPortalType']
if listbox_kw.get('getTranslatedSimulationStateTitle'):
  kw['translated_simulation_state_title'] = listbox_kw['getTranslatedSimulationStateTitle']
if listbox_kw.get('total_quantity'):
  kw['stock.quantity'] = listbox_kw['total_quantity']
if listbox_kw.get('Movement_getMirrorSectionTitle'):
  kw['stock_mirror_section_title'] = listbox_kw['Movement_getMirrorSectionTitle']
if listbox_kw.get('date'):
  kw['stock.date'] = listbox_kw['date']

if reconciled_uid_list is not None:
  # This is to prevent showing again the lines that we just reconciled
  kw['workaround_catalog_lag_query'] = NegatedQuery(SimpleQuery(uid=reconciled_uid_list))
  
if context.getSourcePayment():
  # As we are showing quantities and not asset prices, we use the precision
  # from this bank account currency.
  # TODO: This should be defined earlier because it does not apply to fast input fields.
  container.REQUEST.set('precision',
      context.getQuantityPrecisionFromResource(
        context.getSourcePaymentValue().getPriceCurrency()))

return context.portal_simulation.getMovementHistoryList(**kw)
