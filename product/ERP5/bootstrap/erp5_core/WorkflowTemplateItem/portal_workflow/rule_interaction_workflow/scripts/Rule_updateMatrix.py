matrix = state_change['object']
if getattr(matrix, 'updateMatrix', None) is not None:
  matrix.activate(
    after_path_and_method_id=([matrix.getPath(),],
        ['immediateReindexObject', 'recursiveImmediateReindexObject'])
    ).updateMatrix()
