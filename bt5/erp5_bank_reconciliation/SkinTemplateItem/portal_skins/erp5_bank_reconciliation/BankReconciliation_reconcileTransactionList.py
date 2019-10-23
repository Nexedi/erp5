from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()

# Update selected uids. Required when the user select lines from different pages
portal.portal_selections.updateSelectionCheckedUidList(list_selection_name, listbox_uid, uids)
selection_uid_list = portal.portal_selections.getSelectionCheckedUidsFor(list_selection_name)

reconciled_bank_account = context.getSourcePayment()

if reconciliation_mode == 'reconcile':
  line_list = []
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
        context.Base_updateDialogForm()
        request = container.REQUEST
        request.form['reset'] = 1
        request.form['cancel_url'] = cancel_url
        request.form['field_your_reconciliation_mode'] = reconciliation_mode
        request.form['reconciliation_mode'] = reconciliation_mode
        return context.Base_renderForm(dialog_id, keep_items={
          'portal_status_message': translateString("Line Already Reconciled")})

    line_list.append(line)

  for line in line_list:
    line.AccountingTransactionLine_addBankReconciliation(
          context.getRelativeUrl(),
          message=translateString("Reconciling Bank Line"))

  context.Base_updateDialogForm(update=1)
  request = container.REQUEST
  request.form['reset'] = 1
  request.form['cancel_url'] = cancel_url
  request.form['field_your_reconciliation_mode'] = reconciliation_mode
  request.form['reconciliation_mode'] = reconciliation_mode
  request.form['reconciled_uid_list'] = selection_uid_list
  return context.Base_renderForm(dialog_id, keep_items={
      'portal_status_message': translateString("Lines Reconciled")})

assert reconciliation_mode == 'unreconcile'
for line in portal.portal_catalog(uid=selection_uid_list or -1):
  line = line.getObject()
  line.AccountingTransactionLine_removeBankReconciliation(
      context.getRelativeUrl(),
      message=translateString("Reconciling Bank Line"))

context.Base_updateDialogForm(update=1)
request = container.REQUEST
request.form['reset'] = 1
request.form['cancel_url'] = cancel_url
request.form['field_your_reconciliation_mode'] = reconciliation_mode
request.form['reconciliation_mode'] = reconciliation_mode
request.form['reconciled_uid_list'] = selection_uid_list
return context.Base_renderForm(dialog_id, keep_items={
    'portal_status_message': translateString("Lines Unreconciled")})
