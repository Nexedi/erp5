tag = "afterExport:%s" % state_change['object'].getReference()
method = state_change['object'].getTypeBasedMethod('export')
if method is not None:
  getattr(
    state_change['object'].activate(tag=tag, activity='SQLQueue'), method.id)()
