user_site = context.Baobab_getUserAssignedRootSite()
user_counter = context.Baobab_getUserAssignedSiteList()[0]
if user_site in ('', None) or user_counter in ('', None):
  raise ValueError("Unable to determine site")
if 'guichet' not in user_counter:
  raise ValueError("You are not assigned to a counter")
context.edit(source=user_counter, source_trade=user_site)
