budget = sci['object']
budget_model = budget.getSpecialiseValue(portal_type='Budget Model')
if budget_model is not None:
  budget_model.initializeBudget(budget)
