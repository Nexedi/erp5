agent_list = []
for o in context.objectValues(portal_type='Check Operation Line'):
  bank_account = o.getSourcePaymentValue()
  if bank_account in ('', None):
    continue
  agent_list.extend(bank_account.searchFolder())

return agent_list
