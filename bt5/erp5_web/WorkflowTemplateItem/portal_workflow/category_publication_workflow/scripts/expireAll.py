object = state_change['object']

workflow_tool = object.getPortalObject().portal_workflow

if workflow_tool.isTransitionPossible(object, 'expire'):
  object.expire()

if workflow_tool.isTransitionPossible(object, 'expire_protected'):
  object.expireProtected()

if workflow_tool.isTransitionPossible(object, 'expire_published'):
  object.expirePublished()
