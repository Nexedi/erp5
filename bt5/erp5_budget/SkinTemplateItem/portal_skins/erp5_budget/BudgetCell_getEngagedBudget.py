line = context.getParentValue()
budget = line.getParentValue()
budget_model = budget.getSpecialiseValue(portal_type='Budget Model')
if budget_model is None:
  kw = {}
else:
  kw = budget_model.getInventoryQueryDict(context)

if from_date:
  kw['from_date'] = from_date
if at_date:
  kw['at_date'] = at_date

portal = budget.getPortalObject()
kw.setdefault('stock_explanation_simulation_state',
              portal.getPortalReservedInventoryStateList() +
              portal.getPortalCurrentInventoryStateList() +
              portal.getPortalTransitInventoryStateList())

# XXX use getBudgetConsumptionMethod ?
if src__:
  return '-- %s\n%s' % (kw, portal.portal_simulation.getCurrentInventoryAssetPrice(src__=src__, **kw))
return (portal.portal_simulation.getInventoryAssetPrice(**kw) or 0) * line.BudgetLine_getConsumptionSign()
