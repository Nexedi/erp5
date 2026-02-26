cache_id = '{}.cache'.format(script.getId())
params_cache = context.REQUEST.other.get(cache_id, None)
if params_cache is None:
  params_cache = [("", "")] + [
    (
      context.Base_translateString("${reference} - ${title}", mapping={
        "reference": context.Movement_getSpecificReference(x),
        "title": context.Movement_getExplanationTitle(x),
      }) if context.Movement_getSpecificReference(x) else context.Movement_getExplanationTitle(x),
      x.getUid(),
    )
    for x in context.BankReconciliation_getAccountingTransactionLineList()]

  context.REQUEST.other[cache_id] = params_cache

return params_cache
