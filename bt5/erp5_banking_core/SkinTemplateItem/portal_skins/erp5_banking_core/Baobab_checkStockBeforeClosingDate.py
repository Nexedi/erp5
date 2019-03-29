# Make sure that there is no stock on counters and that there
# is not too much money into the usual cash
# This is usefull when we close a counter date

from Products.ERP5Type.Message import Message
from Products.DCWorkflow.DCWorkflow import ValidationFailed

if site is None:
  root_site_url = context.Baobab_getUserAssignedRootSite()
  site = context.portal_categories.restrictedTraverse(root_site_url)

resource_uid_list = [x.uid for x in context.currency_cash_module.searchFolder()]


counter_vault_list = context.Delivery_getVaultItemList(
    user_site=0,base_site=site.getRelativeUrl(),all=1,
    vault_type=('site/surface/banque_interne','site/surface/gros_paiement',
               'site/surface/gros_versement','site/surface/operations_diverses',
               'site/surface/salle_tri',
               'site/surface/caisse_courante/encaisse_des_devises'))
for counter_vault in counter_vault_list:
  counter_vault_url = counter_vault[1]
  if counter_vault_url=='':
    continue
  counter_title = counter_vault[0]
  inventory_list = context.portal_simulation.getCurrentInventoryList(
                                                     node=counter_vault_url,
                                                     resource_uid=resource_uid_list,
                                                     group_by_resource=1,
                                                     group_by_variation=1,
                                                     ignore_variation=0)
  if len(inventory_list)>0:
    for inventory in inventory_list:
      if inventory.total_quantity>0:
        message = Message(domain='ui',
                    message='Sorry, some resources are still remaining here : $counter_title',
                    mapping={'counter_title':counter_title})
        raise ValidationFailed(message)

max_price = context.portal_preferences.getPreferredUsualCashMaxRenderingPrice()
if max_price is None:
  message = Message(domain='ui',
              message='Sorry, you must defined the max price for the usual cash in your preference')
  raise ValidationFailed(message)

usual_cash = site.getRelativeUrl() + '/surface/caisse_courante/encaisse_des_billets_et_monnaies'
inventory_list = context.portal_simulation.getCurrentInventoryList(
                         node=usual_cash,
                         resource_uid=resource_uid_list)
total_price = sum([x.total_price for x in inventory_list])
context.log('current_price',total_price)

if total_price > max_price:
  message = Message(domain='ui',
              message='Sorry, the amount in the usual cash is too high')
  raise ValidationFailed(message)
