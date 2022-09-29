budget = context.getParentValue()
budget_model = budget.getSpecialiseValue(portal_type='Budget Model')
if budget_model is None:
  return []

if base_id == 'cell':
  return budget_model.getCellRangeForBudgetLine(context, matrixbox=matrixbox)
if base_id in ('engaged', 'available'):
  return budget_model.getConsumptionCellRangeForBudgetLine(context, matrixbox=matrixbox, engaged_budget=True)
if base_id == 'consumed':
  return budget_model.getConsumptionCellRangeForBudgetLine(context, matrixbox=matrixbox, engaged_budget=False)
assert False, "Incorrect base_id %r" % (base_id, )
