"""
================================================================================
Return list of bank accounts for default organisation defined in preferences
================================================================================
"""
# parameters:
# ------------------------------------------------------------------------------
# parameter                          Parameter to lookup

from zExceptions import Unauthorized

preference = context.getPortalObject().portal_preferences

organisation_relative_url = preference.getPreferredCorporateIdentityTemplateDefaultOrganisationRelativeUrl()
if organisation_relative_url:
  try:
    organisation = context.restrictedTraverse(organisation_relative_url)
    return [('', '')] + [(account.getTitle(), account.getRelativeUrl()) for account in organisation.searchFolder(portal_type='Bank Account', sort_on='title')]
  except Unauthorized:
    return None
return None
