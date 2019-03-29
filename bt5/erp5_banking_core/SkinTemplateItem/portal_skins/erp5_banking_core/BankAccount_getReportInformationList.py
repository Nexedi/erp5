from Products.ERP5Type.Message import Message
account = None
portal = context.getPortalObject()
catalog = portal.portal_catalog
portal_type = "Bank Account"

if reference is None:
  message = Message(domain="ui", message="Please give a reference")
  raise ValueError(message)

#context.log('reference',reference)
account_list = catalog(string_index=reference, portal_type=portal_type, validation_state=('valid', 'closed'))
# context.log('sql src',catalog(string_index=reference, portal_type=portal_type, validation_state=('valid', 'closed'),src__=1))
# context.log('len 1',len(account_list))
if len(account_list) == 0:
  account_list = catalog(string_index="%%%s%%" % reference, portal_type=portal_type, validation_state=('valid', 'closed'))
#context.log('len 2',len(account_list))
if len(account_list) == 0:
  message = Message(domain="ui", message="No bank account have this reference")
  raise ValueError(message)
if force_one_account and len(account_list) != 1:
  message = Message(domain="ui", message="More than one account match this research")
  raise ValueError(message)

account_list = [x.getObject() for x in account_list]

if total_price:
  tmp_dict = {}
  new_list = []
  for account in account_list:
    quantity = account.BankAccount_getCurrentPosition()
    tmp_dict['total_price'] = quantity
    new_list.append(account.asContext(**tmp_dict))
  account_list = new_list

# context.log("final account list",account_list)
return account_list
