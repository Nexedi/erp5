task_report = context.getCausalityRelatedValue(portal_type='Task Report')
if task_report is not None:
  return "%s/view" % task_report.absolute_url()
