"""Returns an item list of the acceptable bank accounts.
If `organisation` is passed, then we only show bank accounts available for that
organisation, using the following policy:
 - if organisation contains bank accounts directly, only those bank accounts
   can be selected
 - if organisation higher in the group hierarchy contains bank accounts, bank
   accounts from parent organisations can be selected
 - it means a higher in the group cannot use bank account from organisations
   below, maybe we'll want to change this ...

If organisation is not passed, this script will return all bank accounts
applicable for section_category and section_category_strict_membership.
"""
portal = context.getPortalObject()

search_kw = dict(portal_type=portal.getPortalPaymentNodeTypeList())
if skip_invalidated_bank_accounts:
  search_kw['validation_state'] = '!=invalidated'

if organisation:
  organisation_value = portal.restrictedTraverse(organisation)

  # if organisation contains bank accounts, only take into account those.
  bank_account_list = organisation_value.searchFolder(**search_kw)

    # else we lookup in parent organisations
  if not bank_account_list:
    group_value = organisation_value.getGroupValue(None)
    if group_value is not None:
      uid_list = []
      while group_value.getPortalType() != 'Base Category':
        uid_list.append(group_value.getUid())
        group_value = group_value.getParentValue()
      search_kw['strict_parent_group_uid'] = uid_list
      search_kw['parent_portal_type'] = 'Organisation'
      bank_account_list = portal.portal_catalog(**search_kw)

else:
  if section_category is None:
    section_category = portal.portal_preferences\
        .getPreferredAccountingTransactionSectionCategory()
  section_uid = portal.Base_getSectionUidListForSectionCategory(
                               section_category=section_category,
                               strict_membership=section_category_strict_membership)
  search_kw['parent_uid'] = section_uid
  bank_account_list = portal.portal_catalog(**search_kw)


item_list = [('', '')]
for bank in bank_account_list:
  bank = bank.getObject()
     
  if bank.getReference() and bank.getTitle() \
                  and bank.getReference() != bank.getTitle():
    item_list.append(('%s - %s' % ( bank.getReference(),
                                    bank.getTitle() or 
                                    bank.getSourceFreeText() or
                                    bank.getSourceTitle()),
                                    bank.getRelativeUrl()))
  else:
    item_list.append(( bank.getReference() or
                       bank.getTitle() or 
                       bank.getSourceFreeText() or
                       bank.getSourceTitle(),
                       bank.getRelativeUrl() ))

return item_list
