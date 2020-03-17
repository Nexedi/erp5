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
