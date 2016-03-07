"""
  Find the list of objects to synchronize by calling the catalog.

  Possibly look up a single object based on its ID, GID
"""
account_list = []
if not id:
  for account in context.portal_catalog(portal_type='Account'):
    if account.getReference() and account.getValidationState() != 'deleted':
      account_list.append(account)
  return account_list
account = getattr(context.account_module, id)
if account.getReference() and account.getValidationState() != 'deleted':
  account_list.append(account)
return account_list
