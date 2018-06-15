site = context.getPortalObject()

commit_item_list = context.objectValues()

for item in commit_item_list:
  if site.portal_workflow.isTransitionPossible(item, 'build'):
    site.portal_workflow.doActionFor(item, 'build_action')
