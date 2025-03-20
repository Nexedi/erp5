# default predicate configuration
multimembership_criterion_base_category=["publication_section"]
membership_criterion_category=["publication_section/forum"]
# forum predicate configuration
if forum_relative_url:
  forum = context.restrictedTraverse(forum_relative_url)
  multimembership_criterion_base_category=forum.getMultimembershipCriterionBaseCategoryList()
  membership_criterion_category=forum.getMembershipCriterionCategoryList()

forum.setCategoryList(membership_criterion_category)

context.edit(criterion_property=("portal_type",),
             membership_criterion_base_category=[],
             multimembership_criterion_base_category=multimembership_criterion_base_category,
             membership_criterion_category=membership_criterion_category)
context.setCriterion("portal_type", "Discussion Forum")
