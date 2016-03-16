# XXX must use a cache for this method

emission_letter_dict = {}
user_site_list = []
if site == None :
  if user is not None:
    user_site_list = context.Baobab_getUserAssignedSiteList(user)
  else:
    user_site_list = context.Baobab_getUserAssignedSiteList()
else :
  user_site_list.append(site)

return context.Baobab_getEmissionLetterList(site_list=user_site_list)
