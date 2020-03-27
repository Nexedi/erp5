line = state_change['object']

base_id = 'cell'
line.updateCellRange(base_id=base_id)

# also update membership criterion category list on line
if line.getMembershipCriterionBaseCategoryList():
  line.setMembershipCriterionCategoryList([])
  budget_line_category_list = line.getCategoryList()
  for variation in budget_line_category_list:
    if not variation:
      continue
    base = variation.split('/', 1)[0]
    if base in line.getMembershipCriterionBaseCategoryList():
      line.setMembershipCriterionCategoryList(
            [variation,] + line.getMembershipCriterionCategoryList())
