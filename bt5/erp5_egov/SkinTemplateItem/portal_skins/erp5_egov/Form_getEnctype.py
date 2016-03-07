enctype = getattr(context, "enctype")
if enctype in ('', None):
  return None
return enctype
