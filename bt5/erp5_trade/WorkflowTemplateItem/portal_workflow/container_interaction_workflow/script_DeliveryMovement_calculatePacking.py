document = state_change['object']
delivery = document.getExplanationValue()
if getattr(delivery, 'calculatePacking', None) is not None:
  try:
    container = document.getContainerValue()
  except AttributeError:
    container = None
  if container is None:
    tag = None
  else:
    tag = script.id + '_' + container.getPath()
    # XXX: Tagged reindexation added to replace after_path_and_method_id. May be unnecessary.
    container.recursiveReindexObject(activate_kw={'tag': tag})
  delivery.activate(after_tag=tag).calculatePacking()
