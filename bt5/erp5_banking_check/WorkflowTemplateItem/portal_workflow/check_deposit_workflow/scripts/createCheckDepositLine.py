transaction = state_change['object']

# for outgoing line, must recreate them all because their number can have change
out_line_list = transaction.contentValues(filter = {'portal_type' : 'Outgoing Check Deposit Line'})
if len(out_line_list) != 0:
  id_list = [x.getId() for x in out_line_list]
  transaction.manage_delObjects(id_list)
  
# one for each source/check operation line
for check_operation_line in transaction.contentValues(filter = {'portal_type' : 'Check Operation Line'}):
  source_bank_account = check_operation_line.getSourcePaymentValue()
  # immediate reindex is required to make this operation atomic.
  transaction.newContent(portal_type = 'Outgoing Check Deposit Line',
                         source_credit = check_operation_line.getPrice(),
                         source_payment_value = source_bank_account,)
  # this prevents multiple transactions from being committed at the same time for this bank account.
  source_bank_account.serialize()

# for the incoming line, create it if needed and update it
in_line_list = transaction.contentValues(filter = {'portal_type' : 'Incoming Check Deposit Line'})
if len(in_line_list) == 0:
  transaction.newContent(portal_type = 'Incoming Check Deposit Line',)
  in_line_list = transaction.contentValues(filter = {'portal_type' : 'Incoming Check Deposit Line'})

line = in_line_list[0]
line.setSourceCredit(transaction.getSourceTotalAssetPrice())
line.setDestinationPaymentValue(transaction.getDestinationPaymentValue())
