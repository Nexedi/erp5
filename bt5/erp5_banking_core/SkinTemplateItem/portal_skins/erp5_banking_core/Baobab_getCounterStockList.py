from Products.ERP5Type.Message import Message
from Products.DCWorkflow.DCWorkflow import ValidationFailed

if site is None:
  if getattr(context,'getSiteValue',None) is not None:
    site = context.getSiteValue()
if site is None:
  root_site_url = context.Baobab_getUserAssignedRootSite()
  site = context.portal_categories.restrictedTraverse(root_site_url)

resource_uid_list = [x.uid for x in context.currency_cash_module.searchFolder()]


counter_vault_list = context.Delivery_getVaultItemList(
    user_site=0,base_site=site.getRelativeUrl(),all=1,
    vault_type=('site/surface/banque_interne','site/surface/gros_paiement',
               'site/surface/gros_versement','site/surface/operations_diverses',
               'site/surface/salle_tri'))
counter_vault_list.extend(context.Delivery_getVaultItemList(
    user_site=0,base_site=site.getRelativeUrl(),all=1,
    vault_type=('site/surface/caisse_courante',)))
total_inventory_list = []
for counter_vault in counter_vault_list:
  counter_title = counter_vault[0]
  counter_vault_url = counter_vault[1]
  if counter_vault_url in ('', None):
    continue
  counter_title = counter_vault[0]
  temp_list = context.CounterModule_getVaultTransactionList(vault=counter_vault_url)
  for temp_object in temp_list:
    temp_object.setProperty('counter_title',counter_title)
  total_inventory_list.extend(temp_list)

return total_inventory_list
