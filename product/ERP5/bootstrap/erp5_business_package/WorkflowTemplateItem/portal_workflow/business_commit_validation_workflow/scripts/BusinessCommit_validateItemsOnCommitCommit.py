site = context.getPortalObject()

commit = state_change['object']
commit_item_list = commit.objectValues()

for item in commit_item_list:
  if site.portal_workflow.isTransitionPossible(item, 'validate'):
    site.portal_workflow.doActionFor(item, 'validate_action')
  elif site.portal_workflow.isTransitionPossible(item, 'delete'):
    site.portal_workflow.doActionFor(item, 'delete_action')
