budget_model = context.getSpecialiseValue(portal_type='Budget Model')
if budget_model is not None:
  return budget_model.getBudgetVariationRangeCategoryList(context)

return []
