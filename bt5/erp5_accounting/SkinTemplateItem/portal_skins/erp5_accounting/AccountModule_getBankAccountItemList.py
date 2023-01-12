"""Returns an item list of the acceptable bank accounts.
If `organisation` is passed, then we only show bank accounts available for that
organisation, using the following policy:
 - if organisation is independent accounting entity (ie. have accounting periods),
   only bank accounts from this organisation can be selected.
 - otherwise, bank accounts from this organisation and all organisation directly
   members of the parent groups can be used
 - if organisation higher in the group hierarchy contains bank accounts, bank
   accounts from parent organisations can be selected

`organisation` can actually be a person or other portal types, in this case they
are assumed to be independent accounting entities.

If organisation is not passed, this script will return all bank accounts
applicable for section_category and section_category_strict_membership.

If `base_category` is passed, the currently linked bank account with the specified
base_category is anyway included.
"""
from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()


search_kw = dict(
  portal_type=portal.getPortalPaymentNodeTypeList(),
  validation_state='validated',
)

if organisation:
  entity_value = portal.restrictedTraverse(organisation)
  # if entity is an independent accounting section and contains bank accounts,
  # only take into account those.
  if entity_value.getPortalType() != 'Organisation' \
      or entity_value == entity_value.Organisation_getMappingRelatedOrganisation():
    bank_account_list = entity_value.searchFolder(**search_kw)
  # else we lookup in organisations from parent groups.
  else:
    group_value = entity_value.getGroupValue(None)
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


# If we have bank accounts from more than one entity, include
# the entity as hierarchy to show which entity the bank
# account belongs to.
include_entity_hierarchy = len(set(
  ['/'.join(b.path.split('/')[:-1]) for b in bank_account_list])) > 1

bank_account_list = [brain.getObject() for brain in sorted(
  bank_account_list, key=lambda b:b.path
)]


def getItemList(bank_account, warning=False):
  reference = bank_account.getReference()
  title = bank_account.getTitle() or bank_account.getSourceFreeText() or bank_account.getSourceTitle()
  label = title
  if reference != title:
    label = '{} - {}'.format(reference, title)
  if warning:
    label = '??? ({})'.format(label)
  return (label, bank_account.getRelativeUrl())


previous_entity = None
# sort bank accounts in a way that bank accounts from the same
# entity are consecutive
for bank in bank_account_list:
  if include_entity_hierarchy:
    entity = bank.getParentValue()
    if entity != previous_entity:
      previous_entity = entity
      # include non-selectable element to show hierarchy
      item_list.append((entity.getTranslatedTitle(), None))
  item_list.append(getItemList(bank))

if base_category is not None:
  current_value = context.getProperty(base_category + '_value')
  if current_value and current_value not in bank_account_list:
    item_list.append((
      translateString(
        'Invalid bank account from ${entity_title}',
        mapping={'entity_title': current_value.getParentTitle()}), None))
    item_list.append(getItemList(current_value, warning=True))

return item_list
