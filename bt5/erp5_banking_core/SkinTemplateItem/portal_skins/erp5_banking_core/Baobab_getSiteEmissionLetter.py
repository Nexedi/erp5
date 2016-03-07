# Rerturns the emission letter corresponding to a particular site
from Products.ERP5Type.Cache import CachingMethod

def getSiteEmissionLetter(site=None):
  portal = context.getPortalObject()
  site_object = portal.portal_categories.restrictedTraverse(site)
  lower_letter = site_object.getCodification()[0].lower()
  if lower_letter == 'z':
    lower_letter = 'k'
  return lower_letter

getSiteEmissionLetter = CachingMethod(getSiteEmissionLetter,
                             id = 'Baobab_getSiteEmissionLetter',
                             cache_factory = 'erp5_ui_long')

if not same_type(site, 'a'):
  site = site.getRelativeUrl()

return getSiteEmissionLetter(site=site)
