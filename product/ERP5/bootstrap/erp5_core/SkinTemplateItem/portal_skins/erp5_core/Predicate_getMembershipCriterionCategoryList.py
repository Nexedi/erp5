membership_base_list = context.getMembershipCriterionBaseCategoryList()
multimembership_base_list = context.getMultimembershipCriterionBaseCategoryList()
mixed_list = membership_base_list

for item in multimembership_base_list :
  if item not in mixed_list :
    mixed_list.append(item)

category_list = []

ctool = context.portal_categories
for item in mixed_list:
  base_category = ctool[item]
  item_list = base_category.getCategoryChildCompactLogicalPathItemList(base=1)[:]
  if item_list == [['', '']]:
    for fallback_category_id in base_category.getFallbackBaseCategoryList():
      fallback_category = ctool.restrictedTraverse(fallback_category_id, None)
      if fallback_category is not None and fallback_category.objectIds():
        item_list.extend([('%s/%s' % (fallback_category_id, x[0]), '%s/%s' % (item, x[1])) \
          for x in fallback_category.getCategoryChildCompactLogicalPathItemList(base=1) if x[0]])
        break

  category_list.extend(item_list)

return category_list
