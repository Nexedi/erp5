if editor in (None, ''): 
  return 1

reference = editor

bank_account_list = context.portal_catalog(portal_type="Bank Account", string_index=reference)

if len(bank_account_list) != 1:
  return 0

return 1
