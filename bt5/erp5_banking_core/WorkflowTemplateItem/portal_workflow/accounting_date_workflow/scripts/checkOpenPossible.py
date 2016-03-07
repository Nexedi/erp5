# Check that it is possible to open the accounting date.

from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message
from DateTime import DateTime

now = DateTime()
accounting_date = state_change['object']

# Check that site is defined on accounting_date
site_uid = accounting_date.getSiteUid()
if site_uid is None:
  msg = Message(domain='ui',message="Sorry, the site is not defined")
  raise ValidationFailed (msg,)

opened_date_list = accounting_date.portal_catalog(portal_type="Accounting Date", simulation_state="opened", default_site_uid=accounting_date.getSiteUid())
if len(opened_date_list) > 0:
  msg = Message(domain='ui',message="Sorry, another accounting date is already opened")
  raise ValidationFailed (msg,)
