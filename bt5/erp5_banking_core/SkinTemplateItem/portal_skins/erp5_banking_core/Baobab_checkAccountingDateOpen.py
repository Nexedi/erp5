# Raise ValidationFailed if the accounting date is not opened for the given date and the given site

from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message
from DateTime import DateTime

if date is None:
  # get current date
  date = DateTime()

# Make sure we have a date with no hours
try:
  date = date.Date()
except AttributeError:
  # Assume that non-date parameter contains the bare date.
  pass

if site is None:
  # get site from user assignment
  site_list = context.Baobab_getUserAssignedSiteList()
  if len(site_list) == 0:
    context.log('Baobab_checkAccountingDateOpen', 'No site found for the user')
    return 0
  else:
    site = site_list[0]

# get only the office, not need of vault
#context.log('Baobab_checkAccountingDateOpen', 'get site for vault %s' %(site))
site = context.Baobab_getVaultSite(site)
accounting_date_list = context.portal_catalog(portal_type='Accounting Date', site_id=site.getId(), simulation_state="opened", sort_on=[("start_date", "DESC")], limit=1)
if len(accounting_date_list) == 0:
  opened_accounting_date = DateTime(DateTime().Date())
else:
  opened_accounting_date = accounting_date_list[0].getStartDate()

if DateTime(date) < opened_accounting_date:
  msg = Message(domain = "ui", message="Transaction date incompatible with opened accounting date ${accounting_date}.", mapping={'accounting_date': opened_accounting_date})
  raise ValidationFailed(msg,)

return "ok"
