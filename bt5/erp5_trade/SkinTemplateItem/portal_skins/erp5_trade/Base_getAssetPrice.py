from Products.ERP5Type.Document import newTempAccountingTransactionLine
temp_transaction = newTempAccountingTransactionLine(
  context.getPortalObject(),
  "accounting_line",
  source_section=section.getRelativeUrl(),
  resource=source_currency.getRelativeUrl(),
  start_date=delivery.getStartDate(),
)
exchange_rate = source_currency.getPrice(
  context=temp_transaction.asContext(
      categories=[temp_transaction.getResource(base=True),
                  section.getPriceCurrency(base=True)],
  )
)
if exchange_rate:
  return exchange_rate * context.getPrice()
return context.getPrice()
