tag = "afterPrepareExport:%s" % state_change['object'].getReference()
method = state_change['object'].getTypeBasedMethod('afterPrepareExport')
if method is not None:
  getattr(
    state_change['object'].activate(tag=tag, activity='SQLQueue'), method.id)()
