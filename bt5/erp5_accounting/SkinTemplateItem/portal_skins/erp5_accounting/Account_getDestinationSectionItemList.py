node_uid=None
if not account:
  if (hasattr(context, 'getPortalType') and context.getPortalType() == 'Account') :
    node_uid = context.getUid()
elif same_type(account, '') :
  account = context.getPortalObject().restrictedTraverse(account)
  node_uid = account.getUid()


ptype_translated_dict = {}
def translatePortalType(ptype) :
  """Translate portal_type without retrieving the object from ZODB."""
  if not ptype_translated_dict.has_key(ptype) :
    ptype_translated_dict[ptype] = context.Base_translateString(ptype)
  return ptype_translated_dict[ptype]

section_uid = []
if section_category:
  section_uid = context.Base_getSectionUidListForSectionCategory(
            section_category, strict_membership=section_category_strict_membership)


item_list = [("", "")]
for entity in context.Account_zDistinctSectionList(node_uid=node_uid,
                                                   section_uid=section_uid):
  item_list.append(("%s (%s)" % ( entity['title'],
                                  translatePortalType(entity['portal_type'])),
                                  entity['relative_url']))

return item_list
