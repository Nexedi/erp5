from Products.ERP5Form.Report import ReportSection
path = context.getPhysicalPath()
portal_workflow = context.getPortalObject().portal_workflow
return [
  ReportSection(
    form_id="Base_viewWorkflowHistory",
    level=1,
    listbox_display_mode="FlatListMode",
    path=path,
    selection_params={
      "workflow_id": workflow_id,
      "workflow_title": portal_workflow[workflow_id].title or workflow_id},
    temporary_selection=False)
  for workflow_id in sorted(context.Base_getWorkflowHistory())
]
