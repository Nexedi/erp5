# check that accounting date is opened for the site in which is the counter
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

kwd = {'portal_type' : 'Counter Date', 'simulation_state' : 'open', 'site_uid' : site.getUid()}
date_list = [x.getObject() for x in context.portal_catalog(**kwd)]

if len(date_list) == 0:
  msg = Message(domain='ui', message="Counter date is not opened.")
  raise ValidationFailed(msg,)
