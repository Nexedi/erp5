cat_value = context.getPortalObject().portal_categories.getCategoryValue
return '/'.join([cat_value(x).getTitle() \
  for x in context.getMembershipCriterionCategoryList()])
