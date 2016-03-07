# return counter list for a given site and a given vault type

if vault_type is None:
  vault_type = ('site/surface/banque_interne', 'site/surface/gros_paiement', 'site/surface/gros_versement', 'site/surface/operations_diverses')


vault_list = context.Delivery_getVaultItemList(vault_type=vault_type, strict_membership = 0, leaf_node=0, user_site=1, with_base=0)
counter_dict = {}
for vault in vault_list:
  if len(vault[0].split("/")) == 4:
    counter = '/'.join(vault[0].split("/")[:3])
    if not counter_dict.has_key(counter):
      if not 'siege' in vault[1]:
        counter_dict[counter] = '/'.join(vault[1].split("/")[:6])
      else:
        counter_dict[counter] = '/'.join(vault[1].split("/")[:5])
             

list = counter_dict.items()
list.sort()
return list
