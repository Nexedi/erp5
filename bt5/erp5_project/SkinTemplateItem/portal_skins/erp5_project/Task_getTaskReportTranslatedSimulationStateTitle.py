task_report = context.getCausalityRelatedValue(portal_type='Task Report')
if task_report is not None:
  return task_report.getTranslatedSimulationStateTitle()
