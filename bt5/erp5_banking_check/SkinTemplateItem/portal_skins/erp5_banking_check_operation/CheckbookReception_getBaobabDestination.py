destination = None
# if import, then set destination to None
if not context.isImported():
  destination = context.getDestination()
  if destination is not None:
    destination += '/caveau/auxiliaire/encaisse_des_billets_et_monnaies'

return destination
