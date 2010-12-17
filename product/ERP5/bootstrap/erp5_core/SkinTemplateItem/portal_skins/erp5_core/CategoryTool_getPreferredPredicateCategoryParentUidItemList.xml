<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="PythonScript" module="Products.PythonScripts.PythonScript"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>Script_magic</string> </key>
            <value> <int>3</int> </value>
        </item>
        <item>
            <key> <string>_bind_names</string> </key>
            <value>
              <object>
                <klass>
                  <global name="NameAssignments" module="Shared.DC.Scripts.Bindings"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>_asgns</string> </key>
                        <value>
                          <dictionary>
                            <item>
                                <key> <string>name_container</string> </key>
                                <value> <string>container</string> </value>
                            </item>
                            <item>
                                <key> <string>name_context</string> </key>
                                <value> <string>context</string> </value>
                            </item>
                            <item>
                                <key> <string>name_m_self</string> </key>
                                <value> <string>script</string> </value>
                            </item>
                            <item>
                                <key> <string>name_subpath</string> </key>
                                <value> <string>traverse_subpath</string> </value>
                            </item>
                          </dictionary>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>_body</string> </key>
            <value> <string>#\n
# This script is used by portal_catalog/erp5_mysql_innodb/z_catalog_predicate_category_list\n
#\n
enabled_base_category_list = document.getBaseCategoryList()\n
\n
preferred_predicate_category_list = context.portal_preferences.getPreferredPredicateCategoryList()\n
\n
category_parent_uid_item_list = context.getCategoryParentUidList(membership_criterion_category_list)\n
\n
if not preferred_predicate_category_list:\n
  return category_parent_uid_item_list\n
\n
# category_parent_uid_item_list structure is (category_uid, base_category_uid, category_strict_membership)\n
category_parent_uid_item_dict = {}\n
for category_uid, base_category_uid, category_strict_membership in category_parent_uid_item_list:\n
  if not base_category_uid in category_parent_uid_item_dict:\n
    category_parent_uid_item_dict[base_category_uid] = []\n
  category_parent_uid_item_dict[base_category_uid].append([category_uid, base_category_uid, category_strict_membership])\n
\n
for base_category_id in preferred_predicate_category_list:\n
  base_category = getattr(context, base_category_id, None)\n
  if base_category is None:\n
    continue\n
  base_category_uid = base_category.getUid()\n
\n
  if not base_category_uid in category_parent_uid_item_dict and base_category_id in enabled_base_category_list:\n
    # Add an empty record only if document does not have the category value and the category is enabled on the document.\n
    category_parent_uid_item_dict[base_category_uid] = [[0, base_category_uid, 1]]\n
\n
uid_item_list_list = category_parent_uid_item_dict.values()\n
if uid_item_list_list:\n
  return reduce(lambda a,b:a+b, uid_item_list_list)\n
return ()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>membership_criterion_category_list, document</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CategoryTool_getPreferredPredicateCategoryParentUidItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
