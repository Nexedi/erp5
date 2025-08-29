forum = context
category_list = []

# get the predicate configuration
multi_membership_criterion_category = forum.getMultimembershipCriterionBaseCategoryList()
membership_criterion_category = forum.getMembershipCriterionCategoryList()
for base_category in multi_membership_criterion_category:
  category_list.extend([x for x in membership_criterion_category if x.startswith(base_category)])

forum.setCategoryList(category_list)
