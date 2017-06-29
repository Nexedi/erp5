document = state_change['object']

workflow_tool = document.getPortalObject().portal_workflow

if workflow_tool.isTransitionPossible(document, 'expire'):
  document.expire()

if workflow_tool.isTransitionPossible(document, 'expire_protected'):
  document.expireProtected()

if workflow_tool.isTransitionPossible(document, 'expire_published'):
  document.expirePublished()
