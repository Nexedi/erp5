from Products.PythonScripts.standard import url_quote

REQUEST = container.REQUEST
RESPONSE = REQUEST.RESPONSE
workflow_list = kw.get('workflow_list')
selected_workflow_list = []
selected_workflow_id_list = []

if batch_mode == False and workflow_id_list is None:
  if workflow_list:
    for workflow in workflow_list:
      if workflow.get('listbox_selected'):
        selected_workflow_list.append(context.restrictedTraverse(workflow.get('listbox_key')))

  if len(selected_workflow_list) == 0:
    return context.REQUEST.RESPONSE.redirect(
             '%s/WorkflowTool_viewWorkflowConversion?'
             'portal_status_message=%s' % ( context.absolute_url(),
                                 url_quote('No Workflow Selected.')))
else:
  for workflow_id in workflow_id_list:
    selected_workflow_list.append(getattr(context, workflow_id))

for workflow in selected_workflow_list:
  if workflow is not None and not workflow.isTempObject() and workflow.getPortalType() == 'Workflow':
    return context.REQUEST.RESPONSE.redirect(
             '%s/WorkflowTool_viewWorkflowConversion?'
             'portal_status_message=%s' % ( context.absolute_url(),
                                 url_quote('workflow(s) is already exist.')))
  if workflow is not None and not workflow.isTempObject() and workflow.getPortalType() == 'Interaction Workflow':
    return context.REQUEST.RESPONSE.redirect(
             '%s/WorkflowTool_viewWorkflowConversion?'
             'portal_status_message=%s' % ( context.absolute_url(),
                                 url_quote('workflow(s) is already exist.')))

  # conversion and reassignment
  new_workflow = context.dc_workflow_asERP5Object(workflow, is_temporary=False)
  context.reassignWorkflow(new_workflow.getId())
  selected_workflow_id_list.append(new_workflow.getId())

if batch_mode:
  return

return RESPONSE.redirect("%s/view?portal_status_message=Workflow+%s+converted"
                         %(context.absolute_url(), ',+'.join(selected_workflow_id_list)))
