transaction = state_change['object']

banking_operation_line_list = transaction.contentValues(filter = {'portal_type' : 'Banking Operation Line'})
if len(banking_operation_line_list) != 0:
  id_list = [x.getId() for x in banking_operation_line_list]
  transaction.manage_delObjects(id_list)
# one for each source
for check_operation_line in transaction.contentValues(filter = {'portal_type' : 'Check Operation Line'}):
  source_bank_account = check_operation_line.getSourcePaymentValue()
  # immediate reindex is required to make this operation atomic.
  transaction.newContent(portal_type = 'Banking Operation Line',
                         source_credit = check_operation_line.getPrice(),
                         source_payment_value = source_bank_account,)
  # this prevents multiple transactions from being committed at the same time for this bank account.
  source_bank_account.serialize()
