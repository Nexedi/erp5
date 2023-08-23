from Products.ERP5Type.Utils import UpperCase

portal = context.getPortalObject()
workflow_tool = portal.portal_workflow

for workflow in workflow_tool.getWorkflowValueListFor(context):
  if workflow.getPortalType() != 'Interaction Workflow' \
    and workflow.getId() != 'edit_workflow':
    return getattr(context, 'getTranslated%sTitle' % UpperCase(workflow.getStateVariable()))()
