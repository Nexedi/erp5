if context.ExpenseRecord_isRecordReadyForProcess():
  if context.getSimulationState() == "draft" and context.getModificationDate() < DateTime() - 1:
    context.cancel()
