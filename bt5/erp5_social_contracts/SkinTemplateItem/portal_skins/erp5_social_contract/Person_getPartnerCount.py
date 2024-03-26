""" Get the partner count for a person.
 * valid_social_contract_type_list an optional list of type of social contract list to
take into account, if not specified, all type of social contract are valid.
"""
if at_date is None :
  import DateTime
  at_date = DateTime.DateTime()

social_contract_list = []

# find all social contracts.
for social_contract in context.getDestinationRelatedValueList(portal_type='Social Contract'):
  if social_contract.getValidationState() != 'validated':
    continue
  if valid_social_contract_type_list is not None :
    for valid_social_contract_type in valid_social_contract_type_list :
      if social_contract.getSocialContractType() == valid_social_contract_type:
        # XXX access stop_date directly because of wrong acquisition start_date -> stop_date
        if getattr(social_contract, 'stop_date', None) is None or social_contract.stop_date >= at_date:
          social_contract_list.append(social_contract)
        break
  else:
    # XXX access stop_date directly because of wrong acquisition start_date -> stop_date
    if getattr(social_contract, 'stop_date', None) is None or social_contract.stop_date >= at_date:
      social_contract_list.append(social_contract)

partner_uid_set = set()
# find all partners from those social contracts
for social_contract in social_contract_list:
  for partner_uid in social_contract.getDestinationUidList( portal_type = 'Person' ):
    if partner_uid != context.getUid():
      partner_uid_set.add(partner_uid)

return len(partner_uid_set)
