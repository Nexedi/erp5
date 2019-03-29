from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']

source_object = transaction.getSourceValue()
vault = source_object.getPhysicalPath()

# check again that we are in the good accounting date
if check_source_counter_date:
  transaction.Baobab_checkCounterDateOpen(site=source_object, date=transaction.getStartDate())

if 'encaisse_des_externes' not in vault and \
      'encaisse_des_billets_retires_de_la_circulation'  not in vault:
   msg = Message(domain="ui", message="Invalid source.")
   raise ValidationFailed(msg,)

if 'encaisse_des_externes' in vault:
   source_section = transaction.getSourceSection()
   if source_section is None:
     msg = Message(domain="ui", message="Invalid Foreign Agency.")
     raise ValidationFailed(msg,)

 
# In case of dematerialization, we must have only coins
if transaction.isDematerialization():
  for line in transaction.objectValues(portal_type='Monetary Destruction Line'):
    if line.getResourceValue().getPortalType() != 'Coin':
      msg = Message(domain="ui", message="Sorry, dematerialization is possible only with coins.")
      raise ValidationFailed(msg,)

  # Not possible from auxiliary agency
  if 'auxiliaire' in vault:
    msg = Message(domain="ui", message="You can't do this operation on auxiliary site.")
    raise ValidationFailed(msg,)
  
  # Also we must make sure that the source_section is defined
  source_section = transaction.getSourceSection()
  if source_section is None:
    msg = Message(domain="ui", message="Sorry, dematerialization is possible only if the external agency is defined.")
    raise ValidationFailed(msg,)

  if 'encaisse_des_billets_retires_de_la_circulation' not in vault:
    msg = Message(domain="ui", message="Invalid source.")
    raise ValidationFailed(msg,)

  if source_section in source_object.getPath():
    msg = Message(domain="ui", message="You can't used this site.")
    raise ValidationFailed(msg,)
# Check specific for auxiliary agencies
elif "principale" not in vault: 
  site = transaction.getSourceSection()
  if site  in (None, ""):
    msg = Message(domain="ui", message="You must select a foreign agency.")
    raise ValidationFailed(msg,)
  source_country_site = transaction.Baobab_getVaultSite(source_object)
  source_country  = transaction.Baobab_getCountryForSite(source_country_site)
  site_country = transaction.Baobab_getCountryForSite(site)
  if 'encaisse_des_externes' in vault and \
         site_country == source_country:
    msg = Message(domain="ui", message="You must select an agency from a foreign country.")    
    raise ValidationFailed(msg,)
  elif 'encaisse_des_billets_retires_de_la_circulation' in vault and \
         site_country != source_country:    
    msg = Message(domain="ui", message="You must select an agency from the same country.")    
    raise ValidationFailed(msg,)


# Get price and total_price.
amount = transaction.getSourceTotalAssetPrice()
total_price = transaction.getTotalPrice(portal_type=['Monetary Destruction Line','Monetary Destruction Cell'],fast=0)
resource = transaction.CashDelivery_checkCounterInventory(source=source_object.getRelativeUrl(), portal_type='Monetary Destruction Line')

if resource == 2:
  msg = Message(domain="ui", message="No Resource.")
  raise ValidationFailed(msg,)
elif amount != total_price:
  msg = Message(domain="ui", message="Amount differ from total price.")
  raise ValidationFailed(msg,)
elif resource <> 0 :
  msg = Message(domain="ui", message="Insufficient Balance.")
  raise ValidationFailed(msg,)
