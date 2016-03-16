# XXX it might be better to set resource according to source_payment.
context.setResource('currency_module/' + context.Baobab_getPortalReferenceCurrencyID())
user_site_list = context.Baobab_getUserAssignedSiteList()
if len(user_site_list)>0:
  site = context.Baobab_getVaultSite(user_site_list[0])
  site_url = site.getRelativeUrl()
  context.setSite(site_url)
context.assignRoleToSecurityGroup()
