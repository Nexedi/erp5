portal = context.getPortalObject()
if depth:
  category_relative_url = parent.getMembershipCriterionCategory()
else:
  category_relative_url = portal.portal_preferences.getPreference(
    'preferred_' + context.REQUEST['here'].getPortalType().replace(' Module', '').lower().replace(' ', '_') + '_use',
  )
  if not category_relative_url:
    return ()
child_list, resource_list = portal.portal_categories.use.restrictedTraverse(category_relative_url).Category_getUseCategoryListAndResourceList()
domain_list = []
if child_list:
  resource_uid_by_use_uid_dict = {}
  for row in portal.portal_catalog(select_list=['default_use_uid'], default_use_uid=[x.getUid() for x in child_list]):
    resource_uid_by_use_uid_dict.setdefault(row.default_use_uid, []).append(row.uid)
for child in child_list:
  domain = parent.generateTempDomain(id=child.getId())
  domain.edit(
    title=child.getTranslatedTitle(),
    membership_criterion_category=(child.getRelativeUrl(), ),
    domain_generator_method_id=script.id,
  )
  domain.setCriterionPropertyList(['strict_resource_uid'])
  domain.setCriterion('strict_resource_uid', identity=resource_uid_by_use_uid_dict[child.getUid()])
  domain_list.append(domain)
for resource in resource_list:
  domain = parent.generateTempDomain(id=resource.getId())
  domain.edit(
    title=resource.getTranslatedTitle(),
    membership_criterion_base_category=('resource', ),
    membership_criterion_category=('resource/' + resource.getRelativeUrl(), ),
  )
  domain_list.append(domain)
return sorted(domain_list, key=lambda x: x.getTitle())
