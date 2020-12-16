default_system_preference = context.portal_preferences.default_system_preference
default_system_preference.setPreferredProductVariationBaseCategoryList(['size','colour'])
default_system_preference.setPreferredProductIndividualVariationBaseCategoryList(['variation'])
if context.portal_workflow.isTransitionPossible(default_system_preference, 'enable'):
  default_system_preference.enable()
return 'Done'
