current_site = context.Item_getCurrentSiteValue(at_date=at_date)
if current_site is not None:
  return current_site.getTitle()
return None
