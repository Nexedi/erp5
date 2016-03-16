rule = state_change['object'].getParentValue()
if getattr(rule, 'updateMatrix', None) is not None:
  rule.activate(
    after_path_and_method_id=([rule.getPath(),],
        ['immediateReindexObject', 'recursiveImmediateReindexObject'])
    ).updateMatrix()
