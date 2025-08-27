forum = context
category_list = []

# get the predicate configuration
multi_membership_criterion_category = forum.getMultimembershipCriterionBaseCategoryList()
membership_criterion_category = forum.getMembershipCriterionCategoryList()
for base_category in multi_membership_criterion_category:
  category_list.extend([x for x in membership_criterion_category if x.startswith(base_category)])

# keep follow up values before set categories (e.g. old web_section forum for bakcward compatibility)
previous_follow_up_list = forum.getFollowUpList()
forum.setCategoryList(category_list)
new_follow_up_list = list(set(forum.getFollowUpList() + previous_follow_up_list))
forum.setFollowUpList(new_follow_up_list)
