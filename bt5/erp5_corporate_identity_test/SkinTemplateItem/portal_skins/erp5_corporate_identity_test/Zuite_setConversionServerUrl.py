"""
================================================================================
Set preference for template test to textarea
================================================================================
"""
# parameters   (* default)
# ------------------------------------------------------------------------------

# make sure cloudooo is set for pdf conversions on system_preference
conversion_server_url_list = context.portal_preferences.getPreferredDocumentConversionServerUrlList() or ["https://cloudooo.erp5.net"]
system_preference = context.portal_preferences.default_system_preference
system_preference.setPreferredDocumentConversionServerUrlList(conversion_server_url_list)
return "Conversion Server Url set."
