""" 
This script will be called to apply the customization. 
"""
from Products.ERP5Type.Log import log

# Activate the knowledge pads on portal home to enable later the Wendelin 
# Information gadget.
portal = context.getPortalObject()
default_site_preference = getattr(portal.portal_preferences,
                        'default_site_preference', None)
if default_site_preference is not None:
  default_site_preference.setPreferredHtmlStyleAccessTab(True)
  if default_site_preference.getPreferenceState() == "disabled":
    default_site_preference.enable()

# enable automatic approval of Credential Requests only if erp5_wendelin_data_lake is installed
if portal.portal_templates.getInstalledBusinessTemplate("erp5_wendelin_data_lake_ingestion", strict=True) is not None:
  default_system_preference = getattr(portal.portal_preferences,
                                     'default_system_preference', None)
  if default_system_preference is not None:
    default_system_preference.setPreferredCredentialRequestAutomaticApproval(True)
    if default_system_preference.getPreferenceState() == "disabled":
      default_system_preference.enable()

    # change periodicity of respective alarms from default 60 mins to 1 minute
    # so that we can have a default system in which user registration happens instantly
    accept_submitted_credentials = getattr(portal.portal_alarms,
                                          'accept_submitted_credentials', None)
    if accept_submitted_credentials is not None:
      accept_submitted_credentials.setPeriodicityMinuteFrequency(1)
      
# updata local roles (if any)
business_template = context.getSpecialiseValue()

if business_template is not None:
  # update role settings for modules which exists already
  for portal_type in business_template.getTemplatePortalTypeRoleList():
    module_list = portal.contentValues(
                    filter=dict(portal_type=portal_type))
    for module in module_list:
      module.updateLocalRolesOnSecurityGroups()
      print "Updated Role Mappings for: %s(%s) " % (module.getTitle(), module.getPortalType())

log("%s" % printed)
