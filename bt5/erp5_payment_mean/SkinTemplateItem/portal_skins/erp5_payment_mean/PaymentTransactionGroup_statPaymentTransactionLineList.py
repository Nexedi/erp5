from Products.PythonScripts.standard import Object
_, total_quantity = context.PaymentTransactionGroup_getPaymentTransactionLineCountAndStat()
return Object(total_quantity=total_quantity),
