# Raise ValidationFailed if the counter date not opened for the given date and the given site

from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message


if date is None:
  # get current date
  from DateTime import DateTime
  date = DateTime()

# Make sure we have a date with no hours
date = date.Date()

if site is None:
  # get site from user assignment
  site_list = context.Baobab_getUserAssignedSiteList()
  if len(site_list) == 0:
    context.log('Baobab_checkCounterDateOpen', 'No site found for the user')
    return 0
  else:
    site = site_list[0]

# get only the office, not need of vault
#context.log('Baobab_checkCounterDateOpen', 'get site for vault %s' %(site))
site = context.Baobab_getVaultSite(site)

if context.portal_catalog.countResults(portal_type='Counter Date', start_date=date, site_id=site.getId(), simulation_state="open")[0][0] == 0:
  msg = Message(domain = "ui", message="Transaction not in the good counter date")
  raise ValidationFailed(msg,)
