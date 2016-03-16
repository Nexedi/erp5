# We will take the emission letter and find what is the right site
# for it and the return the result

site_item_list = context.Delivery_getVaultItemList(vault_type=('site',),user_site=0,
                                                  with_base=0,strict_membership=1,
                                                  leaf_node=0)
site_path_list = [x[1] for x in site_item_list if x[1]!='' and 'principale' in x[1]]
site_base_category = context.portal_categories.site
for site_path in site_path_list:
  site = site_base_category.restrictedTraverse(site_path)
  if site.getCodification()[:1].lower()==emission_letter:
    return site
return None
