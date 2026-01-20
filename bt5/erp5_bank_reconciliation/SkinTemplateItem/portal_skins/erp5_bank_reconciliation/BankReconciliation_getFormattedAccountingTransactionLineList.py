return [("", "")] + [
  (
    context.Base_translateString("${reference} - ${title}", mapping={
      "reference": context.Movement_getSpecificReference(x),
      "title": context.Movement_getExplanationTitle(x),
    }) if context.Movement_getSpecificReference(x) else context.Movement_getExplanationTitle(x),
    x.getUid(),
  )
  for x in context.getParentValue().BankReconciliation_getAccountingTransactionLineList(cell=context)]
