from DateTime import DateTime

user_site_list = context.Baobab_getUserAssignedSiteList()
if len(user_site_list) == 0:
  raise ValueError("You cannot create a CounterDate if you don't have an assignment.")

site = context.Baobab_getVaultSite(user_site_list[0])
context.setSiteValue(site)
context.setStartDate(DateTime(DateTime().Date()))


context.assignRoleToSecurityGroup()
