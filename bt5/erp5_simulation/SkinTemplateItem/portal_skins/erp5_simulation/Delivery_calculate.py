portal = context.getPortalObject()
if portal.portal_workflow.isTransitionPossible(context, 'calculate'):
  context.calculate(**kw)
else:
  # Make sure no other node is moving the delivery
  # to 'diverged' or 'solved' state.
  context.serializeCausalityState()
