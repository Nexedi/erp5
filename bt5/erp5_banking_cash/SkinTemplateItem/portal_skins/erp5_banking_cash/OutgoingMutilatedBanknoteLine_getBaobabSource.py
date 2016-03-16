if context.getSimulationState() == "delivered":
  return "%s/encaisse_des_billets_et_monnaies/sortante" % (context.getSource(), )
return None
