from erp5.component.module.Log import log

portal = context.getPortalObject()

portal.setTitle("Wendelin Telecom")

default_site_preference = getattr(portal.portal_preferences, 'default_site_preference', None)
if default_site_preference is not None:
  if default_site_preference.getPreferenceState() == 'disabled':
    default_site_preference.enable()

default_system_preference = getattr(portal.portal_preferences, 'default_system_preference', None)
if default_system_preference is not None:
  # Set Data Product Individual Variation preference
  default_system_preference.setPreferredDataProductIndividualVariationBaseCategory('variation')

  # Disable Data Analysis Sharing preference
  default_system_preference.setPreferredEnableDataAnalysisSharing(0)

  if default_system_preference.getPreferenceState() == 'disabled':
    default_system_preference.enable()

# Update security roles from Wendelin Telecom security model
wendelin_telecom_security_model_business_template = portal.portal_templates.getInstalledBusinessTemplate('erp5_wendelin_telecom_security', strict=True)
if wendelin_telecom_security_model_business_template is not None:
  for portal_type in wendelin_telecom_security_model_business_template.getTemplatePortalTypeRoleList():
    portal_type_instance = getattr(portal.portal_types, portal_type)
    print("Updated Role Mappings for: %s" %portal_type)
    portal_type_instance.updateRoleMapping()

business_template = context.getSpecialiseValue()

if business_template is not None:
  # Update local roles for modules which already exist
  for portal_type in business_template.getTemplatePortalTypeRoleList():
    module_list = portal.contentValues(
      filter=dict(portal_type=portal_type)
    )
    for module in module_list:
      module.updateLocalRolesOnSecurityGroups()
      print("Updated Role Mappings for: %s (%s) " % (module.getTitle(), module.getPortalType()))

log("%s" % printed)
