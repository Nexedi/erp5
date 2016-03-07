budget = context.getParentValue()
budget_model = budget.getSpecialiseValue(portal_type='Budget Model')
if budget_model is not None:
  return budget_model.getBudgetLineVariationRangeCategoryList(context)

return []
