portal = context.getPortalObject()
site_vault_type_uid = portal.portal_categories.vault_type.site.getUid()
result = []
append = result.append
for site in portal.portal_catalog(
  portal_type='Category',
  strict_vault_type_uid=site_vault_type_uid):
  if '/portal_categories/site/' not in site.path:
    continue
  append(site.getObject())
return result
