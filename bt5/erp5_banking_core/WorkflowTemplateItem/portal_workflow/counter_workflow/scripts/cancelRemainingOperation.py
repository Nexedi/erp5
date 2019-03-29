# check that every operation assigned to the counter are delivered
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message
# XXX maybe raise other exception as otherwise the transition will passed even if
# check fail

transaction = state_change['object']
site = transaction.Baobab_getVaultSite(vault=transaction.getSiteValue())

# get the current counter date
kwd = {'portal_type' : 'Counter Date', 'simulation_state' : 'open', 'site_uid' : site.getUid()}
date_list = [x.getObject() for x in context.portal_catalog(**kwd)]
current_date = None
if len(date_list) == 0:
  msg = Message(domain = 'ui', message = 'No Counter Date found for this counter')
  raise ValidationFailed(msg,)
else:
  current_date = date_list[0].getStartDate()

# We should not reject automatically
# I (seb) do not recommand this
#site_uid = transaction.getSiteUid()

#operation_list_object = transaction.Baobab_getRemainingOperationList(site_uid=site_uid, date=current_date, simulation_state=['confirmed',])

#for operation in operation_list_object:
#  operation.reject()
