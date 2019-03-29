from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']

vault = transaction.getSource()


if not (vault.endswith('encaisse_des_billets_et_monnaies') or vault.endswith('encaisse_des_externes')or \
  'encaisse_des_devises' in vault):
   msg = Message(domain="ui", message="Invalid source.")
   raise ValidationFailed(msg,)

root_site = context.Baobab_getVaultSite(vault)
site_emission_letter = context.Baobab_getSiteEmissionLetter(site=root_site)
if vault.endswith('encaisse_des_externes'):
  for line in transaction.getMovementList(portal_type=['Outgoing Cash Balance Regulation Line','Cash Delivery Cell']):
    if line.getEmissionLetter() == site_emission_letter:
      msg = Message(domain="ui", message="You must not select the local emission letter.")
      raise ValidationFailed(msg,)

# check resource between line and document
doc_resource = transaction.getResource()
resource_type = None
for line in transaction.contentValues(portal_type=['Outgoing Cash Balance Regulation Line',
                                                   'Incoming Cash Balance Regulation Line']):
   res = line.getResourceValue()
   if res.getPriceCurrency() != doc_resource:
      msg = Message(domain="ui", message="Resource defined on document is different from input cash.")
      raise ValidationFailed(msg,)
   if resource_type is not None and res.getPortalType() != resource_type:
      msg = Message(domain="ui", message="You can't use both banknote and coin on same document.")
      raise ValidationFailed(msg,)
   resource_type = res.getPortalType()

# check again that we are in the good accounting date
transaction.Baobab_checkCounterDateOpen(site=vault, date=transaction.getStartDate())


resource_one = transaction.CashDelivery_checkCounterInventory(source = vault, portal_type='Incoming Cash Balance Regulation Line')
resource_two = transaction.CashDelivery_checkCounterInventory(source = vault, 
                               portal_type='Outgoing Cash Balance Regulation Line', 
                               same_source=1,
                               no_balance_check=1)

#context.log('resource_one', resource_one)
#context.log('resource_two', resource_two)

# Get total_price.
amount = transaction.getSourceTotalAssetPrice()
incoming_total = transaction.getTotalPrice(portal_type =['Incoming Cash Balance Regulation Line','Cash Delivery Cell'],fast=0)
outgoing_total = transaction.getTotalPrice(portal_type =['Outgoing Cash Balance Regulation Line','Cash Delivery Cell'],fast=0)

#context.log('incoming_total', incoming_total)
#context.log('outgoing_total', outgoing_total)

if amount != incoming_total:
  msg = Message(domain="ui", message="Amount differ from total price.")
  raise ValidationFailed(msg,)

if resource_one == 2:
  msg = Message(domain="ui", message="No resource.")
  raise ValidationFailed(msg,)
elif resource_one == 1:
  msg = Message(domain="ui", message="Insufficient Balance.")
  raise ValidationFailed(msg,)

if resource_two == 2:
  msg = Message(domain="ui", message="No resource.")
  raise ValidationFailed(msg,)

if incoming_total != outgoing_total:
  msg = Message(domain="ui", message="No same balance.")
  raise ValidationFailed(msg,)
