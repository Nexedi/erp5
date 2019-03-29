from Products.ERP5Type.Cache import CachingMethod

if not isinstance(site, str):
  site = site.getRelativeUrl()


def getCountry(site):
  site = context.portal_categories.restrictedTraverse(site)
  orga_id = "site_%3s" %(site.getCodification()[:3])
  organisation = context.organisation_module[orga_id]
  country = organisation.getDefaultRegionTitle()
  if country is None:
    raise ValueError("No Region found for site %s / %s defined by organisation %s" %(site.getPath(), site.getCodification(), organisation.getPath()))
  return country


getCountry = CachingMethod(getCountry, id='Baobab_getCountryForSite', cache_factory='erp5_ui_long')

return getCountry(site)
