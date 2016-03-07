site_list = context.Baobab_getUserAssignedSiteList()
if len(site_list) == 0:
  context.log("ClassificationSurvey_init", "unabled to determine site")

site = site_list[0]
site = context.Baobab_getVaultSite(site)
context.setSource("%s/caveau/auxiliaire/encaisse_des_billets_et_monnaies" %(site.getRelativeUrl(),))
