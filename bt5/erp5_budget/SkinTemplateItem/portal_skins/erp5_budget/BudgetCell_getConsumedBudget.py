kw = {}
budget = context.getParentValue().getParentValue()
budget_model = budget.getSpecialiseValue(portal_type='Budget Model')
if budget_model is not None:
  kw = budget_model.getInventoryQueryDict(context)

if from_date:
  kw['from_date'] = from_date
if at_date:
  kw['at_date'] = at_date

 # XXX use getBudgetConsumptionMethod ?
if src__:
  return '-- %s\n%s' % (kw, context.portal_simulation.getCurrentInventoryAssetPrice(src__=src__, **kw))
return (context.portal_simulation.getCurrentInventoryAssetPrice(**kw) or 0) * context.getParentValue().BudgetLine_getConsumptionSign()
