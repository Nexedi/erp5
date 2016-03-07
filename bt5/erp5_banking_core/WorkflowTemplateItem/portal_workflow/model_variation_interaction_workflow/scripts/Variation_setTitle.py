object = state_change['object']

if object.getPrice() is not None:
  object.setTitle('%i' % object.getPrice())
