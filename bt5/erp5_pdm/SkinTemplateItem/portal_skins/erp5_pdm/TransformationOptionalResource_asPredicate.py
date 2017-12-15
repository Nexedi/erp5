membership_criterion_category_list = context.getMembershipCriterionCategoryList()
membership_criterion_base_category_list = context.getMembershipCriterionBaseCategoryList()

for option in context.getOptionList():
  membership_criterion_category_list.append(option)
  membership_criterion_base_category_list.append(option.split('/')[0])

new_context = context.asContext(
    membership_criterion_category=tuple(set(membership_criterion_category_list)),
    membership_criterion_base_category=tuple(set(membership_criterion_base_category_list)))
return new_context
