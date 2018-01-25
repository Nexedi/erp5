matrix = state_change['object']
if getattr(matrix, 'updateMatrix', None) is not None:
  tag = script.id + '_' + matrix.getPath()
  # XXX: Tagged reindexation added to replace after_path_and_method_id. May be unnecessary.
  matrix.recursiveReindexObject(activate_kw={'tag': tag})
  matrix.activate(after_tag=tag).updateMatrix()
