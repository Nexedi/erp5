"""
================================================================================
Return template parameters from portal-preferences (all calls go through here)
================================================================================
"""
# parameters:
# ------------------------------------------------------------------------------
# parameter                          Parameter to lookup

pref = context.getPortalObject().portal_preferences

if parameter == "default_company_relative_url":
  return pref.getPreferredCorporateIdentityTemplateDefaultOrganisationRelativeUrl()
if parameter == "default_theme":
  return pref.getPreferredCorporateIdentityTemplateDefaultTheme()
if parameter == "default_theme_css_url":
  return pref.getPreferredCorporateIdentityTemplateThemeCssRelativeUrl()
if parameter == "fallback_image":
  return pref.getPreferredCorporateIdentityTemplateFallbackLogoRelativeUrl()
