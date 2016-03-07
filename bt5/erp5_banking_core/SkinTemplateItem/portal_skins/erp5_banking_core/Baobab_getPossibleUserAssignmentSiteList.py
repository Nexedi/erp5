# return site of the user and possible counter on wich user can be assigned
# XXX: this script should be named "Assignment_getPossibleSiteList", as it is not used anywhere else
destination_value = context.getDestinationValue()
if destination_value is None:
  # must have an organisation defined to limit site diplayed
  return [['', '']]

site_list = context.Delivery_getVaultItemList(
  user_site=0,
  vault_type=(
    'site',
    'site/surface/banque_interne/guichet',
    'site/surface/gros_paiement/guichet',
    'site/surface/gros_versement/guichet',
    'site/surface/operations_diverses/guichet',
  ),
  first_level=1,
  strict_membership=1,
  leaf_node=0,
  base_site=destination_value.getSite(),
)
return site_list
