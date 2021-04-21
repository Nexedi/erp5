workflow_list = kw.get('workflow_list')
selected_workflow_list = []
selected_workflow_id_list = []

if not batch_mode and workflow_id_list is None:
  if workflow_list:
    for workflow in workflow_list:
      if workflow.get('listbox_selected'):
        selected_workflow_list.append(context.restrictedTraverse(workflow.get('listbox_key')))

  if len(selected_workflow_list) == 0:
    return context.Base_redirect(
        'WorkflowTool_viewWorkflowConversionDialog',
        keep_items=dict(portal_status_message='No Workflow Selected.'))
else:
  for workflow_id in workflow_id_list:
    selected_workflow_list.append(getattr(context, workflow_id))

for workflow in selected_workflow_list:
  if workflow is not None and not workflow.isTempObject() and workflow.getPortalType() in ('Workflow', 'Interaction Workflow'):
    if batch_mode:
      raise RuntimeError('Workflow(s) already exist.')
    else:
      return context.Base_redirect(
        'WorkflowTool_viewWorkflowConversionDialog',
        keep_items=dict(portal_status_message='Workflow(s) already exist.'))

  # conversion and reassignment
  new_workflow = workflow.convertToERP5Workflow(temp_object=False)
  context.reassignWorkflow(new_workflow.getId())
  selected_workflow_id_list.append(new_workflow.getId())

if not batch_mode:
  return context.Base_redirect(
    'view',
     keep_items=dict(portal_status_message="Workflows converted: %s" %
                     ' '.join(selected_workflow_id_list)))
