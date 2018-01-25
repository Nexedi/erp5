rule = state_change['object'].getParentValue()
if getattr(rule, 'updateMatrix', None) is not None:
  tag = script.id + '_' + rule.getPath()
  # XXX: Tagged reindexation added to replace after_path_and_method_id. May be unnecessary.
  rule.recursiveReindexObject(activate_kw={'tag': tag})
  rule.activate(after_tag=tag).updateMatrix()
