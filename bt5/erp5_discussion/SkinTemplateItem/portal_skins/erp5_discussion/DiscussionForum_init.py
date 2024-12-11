#TODO where to get all this criterion?
# - should come from the linked object (e.g. a web section, what else? a project?)
# - should be left to user to edit via Predicate view UI?
membership_criterion_base_category_set = set(context.getMembershipCriterionBaseCategoryList())
multimembership_criterion_base_category_set = set(context.getMultimembershipCriterionBaseCategoryList())
membership_criterion_category_list = context.getMembershipCriterionCategoryList()
multimembership_criterion_base_category_set.update(membership_criterion_base_category_set)
multimembership_criterion_base_category_set.add("publication_section") #TODO: publication_section was the "root predicate" from old web_section way. Should be used, or add another category here?
membership_criterion_base_category_list = []
multimembership_criterion_base_category_list = list(multimembership_criterion_base_category_set)

context.setTitle("Forum")
context.edit(criterion_property=("portal_type",),
             empty_criterion_valid=True,
             membership_criterion_base_category=membership_criterion_base_category_list,
             multimembership_criterion_base_category=multimembership_criterion_base_category_list,
             membership_criterion_category=membership_criterion_category_list + ["publication_section/forum"])
context.setCriterion("portal_type", "Discussion Thread")
