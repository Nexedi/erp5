from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']

destination = transaction.getDestination()
resource = transaction.CashDelivery_checkCounterInventory(source = destination, portal_type='Cash Delivery Line', 
                                                          same_source=1,no_balance_check=1)
#transaction.log("call to CashDelivery_getCounterInventory return", resource)

# use of the constraint : Test cash status line
#vliste = transaction.checkConsistency()
#transaction.log('vliste', vliste)
#if len(vliste) != 0:
#  raise ValidationFailed, (vliste[0].getMessage(),)

user_id = transaction.portal_membership.getAuthenticatedMember().getId()
site_list = context.Baobab_getUserAssignedSiteList(user_id=user_id)
# context.log('validateVaultBalance site_list',site_list)
destination = transaction.getDestination()
baobab_destination = None
for site in site_list:
  site_value = context.portal_categories.getCategoryValue(site)
  if site_value.getVaultType().endswith('guichet') and destination in site:
    baobab_destination = site + '/encaisse_des_billets_et_monnaies/entrante'
    break
destination = baobab_destination
destination_object = context.portal_categories.getCategoryValue(destination)

# check again that we are in the good accounting date
transaction.Baobab_checkCounterDateOpen(site=destination_object, date=transaction.getStartDate())

# check again that the counter is open

context.Baobab_checkCounterOpened(destination)

# Get price and total_price.
price = transaction.getSourceTotalAssetPrice()
cash_detail = transaction.getTotalPrice(portal_type=['Cash Delivery Line','Cash Delivery Cell'],fast=0)
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
