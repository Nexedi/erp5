site_list = context.Baobab_getUserAssignedSiteList()
if len(site_list) == 0:
  raise ValueError("Unable to determine site")

site = site_list[0]
site = context.Baobab_getVaultSite(site)
context.setSource("%s/caveau/auxiliaire/encaisse_des_billets_ventiles_et_detruits" %(site.getRelativeUrl(),))
