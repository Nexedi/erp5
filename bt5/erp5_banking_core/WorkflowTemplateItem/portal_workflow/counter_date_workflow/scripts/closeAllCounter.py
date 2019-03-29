# put all counter in closing state for the given site
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']

site = transaction.getSiteValue()
while True:
  if not hasattr(site, 'getVaultTypeList'):
    msg = Message(domain = 'ui', message = 'The site value is misconfigured; report this to system administrators.')
    raise ValidationFailed(msg,)
  if 'site' in site.getVaultTypeList():
    break
  site = site.getParentValue()

# First make sure there is not any pending operation
transaction.Baobab_checkRemainingOperation(site=site)

# Then make sure there is nothing any more on counters
transaction.Baobab_checkStockBeforeClosingDate(site=site)

current_date = transaction.getStartDate()
counter_list = [x.getObject() for x in context.portal_catalog(portal_type="Counter", simulation_state = ['open', 'closing'], site_uid = site.getUid())]

for counter in counter_list:
  # close the counter, this will cancel not finished operations automatically
  if counter.getSimulationState() == 'open':
    # first go on state closing
    counter.dispose()
  # the close it
  counter.close()
