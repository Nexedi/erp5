"""Returns an item list of the acceptable bank accounts.
If `organisation` is passed, then we only show bank accounts available for that
organisation, using the following policy:
 - if organisation is independant accounting entity (ie. have accounting periods),
   only bank accounts from this organisation can be selected
 - otherwise, bank accounts from this organisation and all organisation directly
   members of the parent groups can be us
 - if organisation higher in the group hierarchy contains bank accounts, bank
   accounts from parent organisations can be selected

If organisation is not passed, this script will return all bank accounts
applicable for section_category and section_category_strict_membership.
"""
portal = context.getPortalObject()

search_kw = dict(portal_type=portal.getPortalPaymentNodeTypeList())
if skip_invalidated_bank_accounts:
  search_kw['validation_state'] = '!=invalidated'

if organisation:
  organisation_value = portal.restrictedTraverse(organisation)

  # if organisation is an independant accounting section and contains bank accounts,
  # only take into account those.
  if organisation_value == organisation_value.Organisation_getMappingRelatedOrganisation():
    bank_account_list = organisation_value.searchFolder(**search_kw)
  # else we lookup in organisations from parent groups.
  else:
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


# If we have bank accounts from more than one organisation, include
# the organisation as hierarchy to show which organisation the bank
# account belongs to.
include_organisation_hierarchy = len(set(
  ['/'.join(b.path.split('/')[:-1]) for b in bank_account_list])) > 1

previous_organisation = None
# sort bank accounts in a way that bank accounts from the same
# organisation are consecutive
for brain in sorted(bank_account_list, key=lambda b:b.path):
  bank = brain.getObject()
  if include_organisation_hierarchy:
    organisation = bank.getParentValue()
    if organisation != previous_organisation:
      previous_organisation = organisation
      # include non-selectable element to show hierarchy
      item_list.append((organisation.getTranslatedTitle(), None))

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
