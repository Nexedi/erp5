from Products.PythonScripts.standard import Object
_, total_quantity = context.PaymentTransactionGroup_getAccountingTransactionLineCountAndStat(kw.get('selection_name'))
return Object(total_quantity=total_quantity),
