account = context

source_payment_set = {}

for line in account.Account_getAccountingTransactionList() :
   movement_path = line.current_transaction_line_path
   movement = context.restrictedTraverse(movement_path)
   source_payment_set[movement.getSourcePayment()] = 1
#   if movement.getSourcePayment() is None : 
#      context.log('Movement getSourcePayment None ', movement.getPath())
return source_payment_set.keys()
