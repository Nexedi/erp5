portal_type = context.getPortalType().lower().replace(' ', '_').replace('_module', '')
domain_root_list = []

base_category_list = context.portal_preferences.getPreference('preferred_%s_variation_base_category_list' % portal_type)
for base_category in base_category_list:
  base_category_title = context.portal_categories.restrictedTraverse(base_category).getTitle()
  domain_root_list.append((base_category, base_category_title))

return domain_root_list
