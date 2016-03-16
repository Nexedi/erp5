section = context.REQUEST.get('current_web_section', context)
kw['portal_type'] = 'Assignment'

membership_criterion_category = section.getMembershipCriterionCategory()
if membership_criterion_category is not None:
  membership_criterion_category = membership_criterion_category.replace('follow_up/', 'destination_project/')

if section.getMembershipCriterionBaseCategoryList() == ['follow_up']:
  section = section.asContext(membership_criterion_base_category = ['destination_project'],
                              membership_criterion_category=[membership_criterion_category])
return section.searchResults(*args, **kw)
