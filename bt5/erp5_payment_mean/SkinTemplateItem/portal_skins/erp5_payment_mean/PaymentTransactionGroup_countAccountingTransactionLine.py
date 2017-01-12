count, _ = context.PaymentTransactionGroup_getAccountingTransactionLineCountAndStat(kw.get('selection_name'))
return ((count, ), )
