# Reindex the given line with a tag so it can be found in the message table.
activate_kw = {}
if source:
  activate_kw['tag'] = context.BankAccount_getMessageTag(line.getSourcePaymentValue())
  line.reindexObject(activate_kw=activate_kw)
else:
  activate_kw['tag'] = context.BankAccount_getMessageTag(line.getDestinationPaymentValue())
  line.reindexObject(activate_kw=activate_kw)
