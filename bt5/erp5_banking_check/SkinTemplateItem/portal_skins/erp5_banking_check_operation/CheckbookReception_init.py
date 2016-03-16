site = context.Baobab_getVaultSite(context.Baobab_getUserAssignedSiteList()[0])
site_url = site.getRelativeUrl()
context.setDestination(site_url)

from DateTime import DateTime
date = DateTime()
context.setStartDate(date)
