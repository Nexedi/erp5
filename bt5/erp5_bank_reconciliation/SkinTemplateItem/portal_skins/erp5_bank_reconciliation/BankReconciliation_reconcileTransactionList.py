from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()

# Update selected uids. Required when the user select lines from different pages
portal.portal_selections.updateSelectionCheckedUidList(list_selection_name, listbox_uid, uids)
selection_uid_list = portal.portal_selections.getSelectionCheckedUidsFor(list_selection_name)

reconciled_bank_account = context.getSourcePayment()

if mode == 'reconcile':
  for line in portal.portal_catalog(uid=selection_uid_list or -1):
    line = line.getObject()
    # Sanity check: line should not already be reconciled.
    # But what can happen is that this line is an internal transaction line that was
    # reconciled for payment on one side but not yet on the other side (ex. reconciled
    # for the bank account used as source_payment, not not bank account used at
    # destination_payment). So we can accept if the line is already reconciled with a
    # bank reconciliation, if that bank reconciliation is using another bank account
    # that the one on this bank reconciliation.
    # To prevent unauthorized errors, we only consider bank reconciliation users can access.
    for existing_bank_reconciliation in line.getAggregateValueList(
          portal_type='Bank Reconciliation',
          checked_permission='Access contents information'):
      if existing_bank_reconciliation.getSourcePayment() == reconciled_bank_account:
        return context.Base_redirect(
            dialog_id,
            abort_transaction=True,
            keep_items={
                'portal_status_message': translateString("Line Already Reconciled"),
                'reset': 1,
                'cancel_url': cancel_url,
                'mode': mode,
                'field_your_mode': mode})
    line.AccountingTransactionLine_addBankReconciliation(
        context.getRelativeUrl(),
        message=translateString("Reconciling Bank Line"))
  return context.Base_redirect(dialog_id, keep_items={
      'portal_status_message': translateString("Lines Reconciled"),
      'reset': 1,
      'cancel_url': cancel_url,
      'field_your_mode': mode,
      'mode': mode,
      'reconciled_uid_list': selection_uid_list})

assert mode == 'unreconcile'
for line in portal.portal_catalog(uid=selection_uid_list or -1):
  line = line.getObject()
  line.AccountingTransactionLine_removeBankReconciliation(
      context.getRelativeUrl(),
      message=translateString("Reconciling Bank Line"))

return context.Base_redirect(dialog_id, keep_items={
    'portal_status_message': translateString("Lines Unreconciled"),
    'reset': 1,
    'cancel_url': cancel_url,
    'field_your_mode': mode,
    'mode': mode,
    'reconciled_uid_list': selection_uid_list})
