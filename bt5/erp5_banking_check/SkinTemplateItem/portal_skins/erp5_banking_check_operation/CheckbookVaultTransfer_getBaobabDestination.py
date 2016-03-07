destination = context.getDestination()
if destination is not None:
  if destination.endswith('surface'):
    destination = '%s/%s' % (destination,'caisse_courante/encaisse_des_billets_et_monnaies')
  if destination.endswith('caveau'):
    destination = '%s/%s' % (destination,'auxiliaire/encaisse_des_billets_et_monnaies')
return destination
