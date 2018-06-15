site = context.getPortalObject()

item = state_change['object']

if item.getValidationState() == 'built':
  site.portal_workflow.doActionFor(item, 'build_action')
