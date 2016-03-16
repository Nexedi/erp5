site_list = [x[1] for x in context.Delivery_getVaultItemList(vault_type=('site',),strict_membership=1,
                                              leaf_node=0,user_site=0) if x[1]!='']
for site in site_list:
  site_value = context.portal_categories.restrictedTraverse(site)
  if site_value.getCodification()==codification:
    return site_value
return None
