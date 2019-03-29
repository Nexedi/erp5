bank_account = context
resource = bank_account.getPriceCurrencyValue()
if resource is None:
  raise AttributeError('No currency defined on %s' % payment)
account_balance = getattr(resource, get_inventory_id)(
  payment_uid=bank_account.getUid(),
  optimisation__=False, # XXX: optimisation disabled as it has bugs
  src__=src__,
)
# XXX: why str() ?
return str(account_balance)
