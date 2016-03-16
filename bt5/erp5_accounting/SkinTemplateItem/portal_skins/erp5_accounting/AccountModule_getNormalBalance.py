total = context.AccountModule_getBalance(brain=brain, selection=selection, **kw)
account = brain.getObject()
if account.isCreditAccount():
  total = - total
return total
