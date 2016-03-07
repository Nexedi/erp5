source = context.getSource()
if source is not None:
  if source.endswith('surface'):
    source = '%s/%s' % (source,'caisse_courante/encaisse_des_billets_et_monnaies')
  if source.endswith('caveau'):
    source = '%s/%s' % (source,'auxiliaire/encaisse_des_billets_et_monnaies')
return source
