# no more pdf reports
return context.AccountingTransactionModule_viewProfitAndLossAsOO(context.REQUEST)

if context.REQUEST.format_raportu=='pdf':
  return context.AccountingTransactionModule_viewProfitAndLossAsPdf(context.REQUEST)
if context.REQUEST.format_raportu=='oo':
  return context.AccountingTransactionModule_viewProfitAndLossAsOO(context.REQUEST)
