current_site = context.Item_getCurrentOriginValue(**kw)
if current_site is not None:
  return current_site.getSourceTitle()
return None
