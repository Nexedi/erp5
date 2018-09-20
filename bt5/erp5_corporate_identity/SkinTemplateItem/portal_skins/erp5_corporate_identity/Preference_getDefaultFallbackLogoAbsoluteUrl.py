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

fallback_logo_relative_url = preference.getPreferredCorporateIdentityTemplateFallbackLogoRelativeUrl()

if fallback_logo_relative_url:
  try:
    return context.restrictedTraverse(fallback_logo_relative_url).absolute_url()
  except Unauthorized:
    return None
return None
