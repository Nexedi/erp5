portal = context.getPortalObject()
REQUEST = context.REQUEST
dc_workflow_id_list = list(context.getTemplateWorkflowIdList()) #it's a tuple!
erp5_workflow_id_list = []
unknown_workflow_id_list = []

# convert DC workflow to ERP5 workflow
for dc_workflow_id in context.getTemplateWorkflowIdList():
  workflow = portal.portal_workflow.get(dc_workflow_id, None)
  if workflow is None:
    # in case of bt not already installed or wrong workflow name
    unknown_workflow_id_list.append(dc_workflow_id)
  elif workflow.getPortalType() in ['DCWorkflowDefinition', 'InteractionWorkflowDefinition']:
      workflow = portal.portal_workflow.dc_workflow_asERP5Object(workflow)

  if workflow and workflow.getPortalType() in ['Workflow', 'Interaction Workflow']:
    dc_workflow_id_list.remove(dc_workflow_id)
    erp5_workflow_id_list.append(dc_workflow_id)

# move what was defined in field "workflows" to field "path"
context.setTemplatePathList(list(context.getTemplatePathList()) + # it's a tuple!
                            [('portal_workflow/%s**' % workflow_id)
                             for workflow_id in erp5_workflow_id_list])
context.setTemplateWorkflowIdList(dc_workflow_id_list)

if REQUEST is not None:
  ret_url = context.absolute_url() + '/' + REQUEST.get('form_id', 'view')
  formatted_message = ''
  if erp5_workflow_id_list:
    formatted_message += '''Conversion of workflows: %s''' % ', '.join(erp5_workflow_id_list)
  if unknown_workflow_id_list:
    formatted_message += 'ERROR: non-installed workflows: %s' % ', '.join(unknown_workflow_id_list)
  if dc_workflow_id_list:
    formatted_message += 'ERROR: unable to convert workflows: %s' % ', '.join(dc_workflow_id_list)
  formatted_message.replace(' ', '+')
  REQUEST.RESPONSE.redirect("%s?portal_status_message=%s"% (ret_url, formatted_message))
