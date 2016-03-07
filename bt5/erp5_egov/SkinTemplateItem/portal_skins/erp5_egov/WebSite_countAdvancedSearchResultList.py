if search_section_path is not None:
  section_value = context.getPortalObject().restrictedTraverse(search_section_path)
  if kw['portal_type'] == ['Assignment'] and \
     section_value.getMembershipCriterionBaseCategoryList() == ['follow_up']:
     # This is a hack to make sure project members are displayed whenever follow_up base
     # category is used
     section_value = section_value.asContext(membership_criterion_base_category = ['destination_project'],
                        membership_criterion_category = [section_value.getMembershipCriterionCategory().replace('follow_up/', 'destination_project/')])
  return section_value.countResults(**kw)

return context.portal_catalog.countResults(**kw)
