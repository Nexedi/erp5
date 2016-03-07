portal_type = context.getPortalType().lower().replace(' ', '_')

base = context.portal_preferences.getPreference('preferred_%s_variation_base_category_list' % portal_type, [])
optional = context.portal_preferences.getPreference('preferred_%s_optional_variation_base_category_list' % portal_type, [])
individual = context.portal_preferences.getPreference('preferred_%s_individual_variation_base_category_list' % portal_type, [])
use_list = context.portal_preferences.getPreference('preferred_%s_use_list' % portal_type, [])

context.edit(variation_base_category_list=base,
    optional_variation_base_category_list=optional,
    individual_variation_base_category_list=individual,
    use_list=use_list)
