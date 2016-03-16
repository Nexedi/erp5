from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()

# Update selected uids. Required when the user select lines from different pages
portal.portal_selections.updateSelectionCheckedUidList(list_selection_name, listbox_uid, uids)
selection_uid_list = portal.portal_selections.getSelectionCheckedUidsFor(list_selection_name)

if mode == 'reconcile':
  for uid in selection_uid_list:
    line = portal.portal_catalog.getObject(uid)
    if line.getAggregate(portal_type='Bank Reconciliation'):
      return context.Base_redirect(dialog_id,
                  abort_transaction=True,
                  keep_items={'portal_status_message': translateString("Line Already Reconciled"),
                              'reset': 1,
                              'cancel_url': cancel_url,
                              'mode': mode,
                              'field_your_mode': mode})
    line.AccountingTransactionLine_setBankReconciliation(context,
      message=translateString("Reconciling Bank Line"))
  return context.Base_redirect(dialog_id, keep_items={
      'portal_status_message': translateString("Line Reconciled"),
      'reset': 1,
      'cancel_url': cancel_url,
      'field_your_mode': mode,
      'mode': mode,
      'reconciled_uid_list': selection_uid_list})

assert mode == 'unreconcile'
for uid in selection_uid_list:
  line = portal.portal_catalog.getObject(uid)
  line.AccountingTransactionLine_setBankReconciliation(None,
    message=translateString("Reconciling Bank Line"))

return context.Base_redirect(dialog_id, keep_items={
    'portal_status_message': translateString("Lines Unreconciled"),
    'reset': 1,
    'cancel_url': cancel_url,
    'field_your_mode': mode,
    'mode': mode,
    'reconciled_uid_list': selection_uid_list})
