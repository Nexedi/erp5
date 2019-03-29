destination = context.getDestination()
if destination is not None:
  return destination
# calculate the destination
# must use owner to know site letter
site_list = context.Baobab_getUserAssignedSiteList(user_id=context.Base_getOwnerId())
for site in site_list:
  if context.portal_categories.getCategoryValue(site).getVaultType().endswith('/guichet'):
    return site + '/encaisse_des_billets_et_monnaies/entrante'
from Products.ERP5Type.Message import Message
message = Message(domain="ui", message="Object owner is not assigned to a counter.")
raise ValueError(message)
