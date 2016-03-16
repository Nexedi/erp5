portal = context.getPortalObject()

search_kw = {
  'simulation_state': simulation_state,
  'accounting_transaction.section_uid': section_uid_list,
  'operation_date': {'query': (from_date, at_date), 'range': 'minngt' },
  'portal_type': portal_type,
}

method_kw = {
  'active_process': this_portal_type_active_process,
  'section_uid_list': section_uid_list,
}

activate_kw = {
  'tag': tag,
  'priority': priority,
}

portal.portal_catalog.searchAndActivate(
  method_id='AccountingTransaction_postFECResult', 
  method_kw=method_kw,
  activate_kw=activate_kw,
  **search_kw)

context.activate(tag=aggregate_tag, after_tag=tag, activity='SQLQueue').AccountingTransactionModule_aggregateFrenchAccountingTransactionFileForPortalType(
  portal_type=portal_type,
  active_process=active_process,
  this_portal_type_active_process=this_portal_type_active_process)
