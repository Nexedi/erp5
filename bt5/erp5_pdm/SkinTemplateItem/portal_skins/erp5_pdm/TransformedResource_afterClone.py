if item == context:
  # When the parent document is being copied, we do not want to reset int index.
  context.Base_initIntIndex(*args,**kw)
