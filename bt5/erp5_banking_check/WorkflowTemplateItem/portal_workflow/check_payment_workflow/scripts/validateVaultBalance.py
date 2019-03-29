from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']
# Compute the source form the vault choosen by
# the accountant and find the counter with the
# user logged in
user_id = transaction.portal_membership.getAuthenticatedMember().getId()
site_list = context.Baobab_getUserAssignedSiteList(user_id=user_id)
# context.log('validateVaultBalance site_list',site_list)
source = transaction.getSource()
baobab_source = None
for site in site_list:
  site_value = context.portal_categories.getCategoryValue(site)
  if site_value.getVaultType().endswith('guichet') and source in site:
    baobab_source = site + '/encaisse_des_billets_et_monnaies/sortante'
    break

if baobab_source is None:
  msg = Message(domain="ui", message="Unable to determine counter from user assignement.")
  raise ValidationFailed(msg,)

source = baobab_source
source_object = context.portal_categories.getCategoryValue(source)

# check again that we are in the good accounting date
transaction.Baobab_checkCounterDateOpen(site=source_object, date=transaction.getStartDate())


# check again that the counter is open

context.Baobab_checkCounterOpened(source)

resource = transaction.CashDelivery_checkCounterInventory(source = source, portal_type='Cash Delivery Line', same_source=1)
#transaction.log("call to CashDelivery_getCounterInventory return", resource)

# Get price and total_price.
price = transaction.getSourceTotalAssetPrice()
cash_detail = transaction.getTotalPrice(portal_type = ('Cash Delivery Line','Cash Delivery Cell'), fast=0)
#transaction.log("price vs cash detail", str((price, cash_detail)))
if resource == 3:
  msg = Message(domain="ui", message="No banknote or coin defined.")
  raise ValidationFailed(msg,)
elif resource == 2:
  msg = Message(domain="ui", message="No resource defined.")
  raise ValidationFailed(msg,)
elif price != cash_detail:
  msg = Message(domain="ui", message="Amount differs from input.")
  raise ValidationFailed(msg,)
elif resource == 1:
  msg = Message(domain="ui", message="Insufficient Balance in counter.")
  raise ValidationFailed(msg,)


transaction.Base_checkCheck(None, None, None, check=transaction.getAggregateValue())
