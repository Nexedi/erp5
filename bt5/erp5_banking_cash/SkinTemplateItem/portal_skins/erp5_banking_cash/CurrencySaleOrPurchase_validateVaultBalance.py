from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

counter_site = context.getSource()
# check we don't change of user
context.Baobab_checkSameUserVault(counter_site)
# check that we are in the good accounting date
context.Baobab_checkCounterDateOpen(site=counter_site,
  date=context.getStartDate())
# check that the counter is open
context.Baobab_checkCounterOpened(counter_site)

if is_currency_sale:
  foreign_currency_portal_type = outgoing_portal_type
  default_currency_portal_type = incoming_portal_type
  total_quantity = context.CurrencySale_getQuantity()
else:
  foreign_currency_portal_type = incoming_portal_type
  default_currency_portal_type = outgoing_portal_type
  total_quantity = context.CurrencyPurchase_getQuantity()

# check if an exchange rate is defined
if total_quantity is None:
  raise ValidationFailed(Message(domain='ui',
    message="No exchange rate defined for this currency at document date."))

# check resource on currency fastinput
doc_resource = context.getResource()
for line in context.contentValues(portal_type=foreign_currency_portal_type):
  if line.getResourceValue().getPriceCurrency() != doc_resource:
    raise ValidationFailed(Message(domain="ui",
      message="Resource defined on document is different from currency cash."),)

# check outgoing amount
if is_currency_sale:
  amount = context.getSourceTotalAssetPrice()
else:
  amount = context.getQuantity()
if amount is None or amount <= 0:
  msg = Message(domain="ui", message="Amount is not valid.")
  raise ValidationFailed(msg,)

# Reverse error messages in cash of currency purchase
default_msg = "Received amount is different from input cash."
foreign_msg = "Return amount is different from output cash"
if not is_currency_sale:
  (default_msg, foreign_msg) = (foreign_msg, default_msg)

# Check default currency amount consistency
if context.getTotalPrice(portal_type=[default_currency_portal_type,
    'Cash Delivery Cell'], fast=0) != context.getQuantity():
  raise ValidationFailed(Message(domain="ui", message=default_msg),)

# Check foreign currency amount consistency
if context.getTotalPrice(portal_type=[foreign_currency_portal_type,
    'Cash Delivery Cell'], fast=0) != context.getSourceTotalAssetPrice():
  raise ValidationFailed(Message(domain="ui", message=foreign_msg),)

# Check outgoing inventory
resource_one = context.CashDelivery_checkCounterInventory(
  portal_type=outgoing_portal_type)
if resource_one == 2:
  raise ValidationFailed(Message(domain="ui", message="No Resource."),)
elif resource_one == 1:
  raise ValidationFailed(Message(domain="ui",
    message="Insufficient balance"),)
