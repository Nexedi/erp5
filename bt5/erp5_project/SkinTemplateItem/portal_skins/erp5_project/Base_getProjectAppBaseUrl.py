# Instance policy: value comes from the preferred_project_management_app_base_url
# System Preference. Empty when unconfigured (callers decide how to handle it).
url = context.getPortalObject().portal_preferences.getPreferredProjectManagementAppBaseUrl("")
return url.rstrip('/')