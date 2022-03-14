movement = state_change['object']
if not movement.isGeneratedBySimulation():
  # A setter was called on a movement that should be linked to
  # a root simulation movement, which usually copies the movement.
  # If there's a new movement in the delivery (e.g. _setObject),
  # the root applied rule must be reexpanded in order to generate
  # the missing simulation movement.
  # XXX: Otherwise, it should be enough to reexpand the related SM.
  movement.getRootDeliveryValue().updateSimulation(expand_root=1)
