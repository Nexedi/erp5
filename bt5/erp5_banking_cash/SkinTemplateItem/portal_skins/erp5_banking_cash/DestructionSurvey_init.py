site = context.Baobab_getUserAssignedRootSite()
if site in ('', None):
  from Products.ERP5Type.Message import Message
  message = Message(domain="ui", message="The owner is not assigned to the right vault.")
  raise ValueError(message)


context.setSource("%s/caveau/auxiliaire/encaisse_des_billets_a_ventiler_et_a_detruire" %(site,))
context.setDestination("%s/caveau/auxiliaire/encaisse_des_billets_ventiles_et_detruits" %(site,))
