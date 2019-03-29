from DateTime import DateTime

user_site_list = context.Baobab_getUserAssignedSiteList()
if len(user_site_list) == 0:
  raise ValueError("You cannot create an AccountingDate if you don't have an assignment.")

site = context.Baobab_getVaultSite(user_site_list[0])
context.setSiteValue(site)
context.setStartDate(DateTime(DateTime().Date()))

# Set a reference
counter_date_list = [x.getObject() for x  in context.portal_catalog(
                                           portal_type='Accounting Date',site_id=site.getSiteId(),
                                           sort_on=[('start_date','descending')],limit=1,
                                           simulation_state=('open','closed'))]
previous_reference = None
if len(counter_date_list)>0:
  previous_counter_date = counter_date_list[0]
  previous_reference = previous_counter_date.getReference()
if previous_reference not in ('',None):
  reference = '%i' % (int(previous_reference)+1)
else:
  reference = '1'
context.setReference(reference)
