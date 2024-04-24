#
# This script is used by portal_catalog/erp5_mysql_innodb/z_catalog_predicate_category_list
#
enabled_base_category_list = document.getBaseCategoryList()

preferred_predicate_category_list = context.portal_preferences.getPreferredPredicateCategoryList()

category_parent_uid_item_list = context.getCategoryParentUidList(membership_criterion_category_list)

if not preferred_predicate_category_list:
  return category_parent_uid_item_list

# category_parent_uid_item_list structure is (category_uid, base_category_uid, category_strict_membership)
category_parent_uid_item_dict = {}
for category_uid, base_category_uid, category_strict_membership in category_parent_uid_item_list:
  if not base_category_uid in category_parent_uid_item_dict:
    category_parent_uid_item_dict[base_category_uid] = []
  category_parent_uid_item_dict[base_category_uid].append([category_uid, base_category_uid, category_strict_membership])

for base_category_id in preferred_predicate_category_list:
  base_category = getattr(context, base_category_id, None)
  if base_category is None:
    continue
  base_category_uid = base_category.getUid()

  if not base_category_uid in category_parent_uid_item_dict and base_category_id in enabled_base_category_list:
    # Add an empty record only if document does not have the category value and the category is enabled on the document.
    category_parent_uid_item_dict[base_category_uid] = [[0, base_category_uid, 1]]

uid_item_list_list = category_parent_uid_item_dict.values()
if uid_item_list_list:
  result = []
  for uid_item_list in uid_item_list_list:
    result.extend(uid_item_list)
  return result

return ()
