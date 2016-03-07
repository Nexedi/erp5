site_list = context.Baobab_getUserAssignedSiteList()
if len(site_list) == 0:
  context.log("MonetaryIsssue_init", "unabled to determine site")

site = site_list[0]
site = context.Baobab_getVaultSite(site)
context.setSource("%s/caveau/serre/encaisse_des_billets_neufs_non_emis" %(site.getRelativeUrl(),))
context.setDestination("%s/caveau/reserve/encaisse_des_billets_et_monnaies" %(site.getRelativeUrl(),))
