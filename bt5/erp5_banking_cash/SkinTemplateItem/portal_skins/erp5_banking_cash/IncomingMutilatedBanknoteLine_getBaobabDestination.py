# When the parent document (Mutilated Banknote) is finished or delivered, the mutilated banknotes must not be put in the "caisse_coutante/billets_mutiles"
# In reality, they are moved to "caisse_courante/billets_mutiles" with "canceled" status.
# To do this, the "mutilated" from "caisse_courante/billets_mutiles" are destroyed from erp5 point of view and new ones with state "canceled" are added to "caisse_courante/encaisse_des_billets_et_monnaies".
# See ExchangedMutilatedBanknoteLine_getBaobabDestination (those lines are created at "planned" state).

mutilated_banknote = context.getParentValue()
if mutilated_banknote.getSimulationState() == 'stopped':
  return mutilated_banknote.getDestination()
return None
