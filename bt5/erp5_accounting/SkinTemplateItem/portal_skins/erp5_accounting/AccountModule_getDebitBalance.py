total = context.AccountModule_getBalance(brain, selection, **kw)
if total > 0.0:
  return total
