count, _ = context.PaymentTransactionGroup_getPaymentTransactionLineCountAndStat(kw.get('selection_name'))
return ((count, ), )
