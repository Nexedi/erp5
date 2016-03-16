object = state_change['object']
delivery = object.getExplanationValue()

activate_kw = {}
if getattr(delivery, 'calculatePacking', None) is not None:
  try:
    container = object.getContainerValue()
    activate_kw['after_path_and_method_id'] = (container.getPath(),
                                         'recursiveImmediateReindexObject')
  except AttributeError:
    pass
  delivery.activate(**activate_kw).calculatePacking()
