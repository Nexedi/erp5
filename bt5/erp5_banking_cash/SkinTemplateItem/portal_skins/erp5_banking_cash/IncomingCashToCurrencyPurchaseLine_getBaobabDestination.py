currency = context.getResourceTitle()
encaisse_devise = "/encaisse_des_devises/%s/sortante" %(context.getParentValue().getResourceTitle('').lower().replace(" ", "_"))
counter_site = context.getSource()
destination = counter_site + encaisse_devise
return destination


# OLD METHOD user logged in
#user_id = context.portal_membership.getAuthenticatedMember().getId()

# NEW METHOD must use owner to know site letter
old_group_list = context.get_local_roles()
for group, role_list in old_group_list:
  if 'Owner' in role_list:
    user_id = group


site_list = context.Baobab_getUserAssignedSiteList(user_id=user_id)
context.log('site_list',site_list)
destination = None
for site in site_list:
  site_value = context.portal_categories.getCategoryValue(site)
  context.log('site_value',site_value)
  if site_value.getVaultType().endswith('guichet') and (('banque_interne' in site) or ('operations_diverses' in site)):
    destination = site + encaisse_devise
    break
context.log('la_bonne_destination',destination)
return destination
