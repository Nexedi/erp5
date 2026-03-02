# Override context to Bank Reconciliation
cell = context
context = cell.getParentValue()

# Cache whole list of possible transaction for the Bank Reconciliation, to make only one catalog query...
cache_id = '{}.cache'.format(script.getId())
params_cache = cell.REQUEST.other.get(cache_id, None)
if params_cache is None:
  params_cache = context.BankReconciliation_getAccountingTransactionLineList()
  cell.REQUEST.other[cache_id] = params_cache

translateString = context.Base_translateString
getSpecificReference = context.Movement_getSpecificReference
getExplanationTitle = context.Movement_getExplanationTitle

start_date = cell.getStartDate()
stop_date = cell.getStopDate()

# ...then narrow down and sort results for the specific line.
movement_list = sorted((mvt for mvt in params_cache \
        if mvt.date >= start_date \
        and mvt.date <= stop_date),
       key=lambda y: abs(y.total_price - cell.getQuantity()))

return [("", "")] + [
  (
    translateString("${reference} - ${title} (${amount})", mapping={
      "reference": getSpecificReference(x),
      "title": getExplanationTitle(x),
      "amount": x.total_price,
    }) if getSpecificReference(x) else getExplanationTitle(x),
    x.getUid(),
  )
  for x in movement_list]
