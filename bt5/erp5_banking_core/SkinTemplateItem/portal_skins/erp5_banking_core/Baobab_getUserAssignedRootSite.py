new_site = context.Baobab_getUserAssignment(user_id=user_id).getSiteValue()
while new_site.getVaultType() != 'site':
  new_site = new_site.getParentValue()
if not object:
  new_site = new_site.getRelativeUrl()
return new_site
