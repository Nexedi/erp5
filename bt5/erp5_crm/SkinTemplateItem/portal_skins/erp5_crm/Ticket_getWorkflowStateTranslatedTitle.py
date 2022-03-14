from Products.ERP5Type.Utils import UpperCase

portal = context.getPortalObject()
workflow_tool = portal.portal_workflow

for workflow in workflow_tool.getWorkflowValueListFor(context):
  # Exclude interaction workflows and edit_workflow
  if workflow.state_var != 'state':
    return getattr(context, 'getTranslated%sTitle' % UpperCase(workflow.state_var))()
