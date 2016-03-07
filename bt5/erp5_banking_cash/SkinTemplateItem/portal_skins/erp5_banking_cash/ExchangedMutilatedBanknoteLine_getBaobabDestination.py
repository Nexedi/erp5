mutilated_banknote = context.getParentValue()
if not(mutilated_banknote.isSentToHeadquaters(False)) and \
   mutilated_banknote.getSimulationState() in ('finished', 'delivered', 'deposited'):
  if mutilated_banknote.getCausality() is None:
    return "%s/encaisse_des_billets_et_monnaies/entrante" % (mutilated_banknote.getSource(), )
  else:
    return "site/%s/surface/caisse_courante/encaisse_des_billets_et_monnaies" % (mutilated_banknote.getSite(), )
return None
