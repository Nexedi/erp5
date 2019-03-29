reference_currency = context.Baobab_getPortalReferenceCurrencyID()
context.setPriceCurrency('currency_module/%s' %(reference_currency,))
context.setCurrencyExchangeType('transfer')
context.setSource(context.getBaobabSource())

movement = context.newContent(portal_type='Banking Operation Line',
                       id='movement',
                       source='account_module/bank_account', # Set default source
                       destination='account_module/bank_account', # Set default destination
                       )

# calculate the source
user_site = None
# must use owner to know site letter
group_list = context.get_local_roles()
for group, role_list in group_list:
  if 'Owner' in role_list:
    user_id = group

site_list = context.Baobab_getUserAssignedSiteList(user_id=user_id)
user_site = None
for site in site_list:
  site_value = context.portal_categories.getCategoryValue(site)
  context.log('site_value',site_value)
  if site_value.getVaultType().endswith('guichet'):
    user_site = site
if user_site is None:
  from Products.ERP5Type.Message import Message
  message = Message(domain="ui", message="The owner is not assigned to the right vault.")
  raise ValueError(message)
context.setSource(user_site)
