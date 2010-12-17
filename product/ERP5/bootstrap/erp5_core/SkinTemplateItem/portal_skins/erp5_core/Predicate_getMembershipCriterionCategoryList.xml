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
            <value> <string>membership_base_list = context.getMembershipCriterionBaseCategoryList()\n
multimembership_base_list = context.getMultimembershipCriterionBaseCategoryList()\n
mixed_list = membership_base_list\n
\n
for item in multimembership_base_list :\n
  if item not in mixed_list :\n
    mixed_list.append(item)\n
\n
category_list = []\n
\n
ctool = context.portal_categories\n
for item in mixed_list:\n
  base_category = ctool[item]\n
  item_list = base_category.getCategoryChildCompactLogicalPathItemList(base=1)[:]\n
  if item_list == [[\'\', \'\']]:\n
    for fallback_category_id in base_category.getFallbackBaseCategoryList():\n
      fallback_category = ctool.restrictedTraverse(fallback_category_id, None)\n
      if fallback_category is not None and fallback_category.objectIds():\n
        item_list.extend([(\'%s/%s\' % (fallback_category_id, x[0]), \'%s/%s\' % (item, x[1])) \\\n
          for x in fallback_category.getCategoryChildCompactLogicalPathItemList(base=1) if x[0]])\n
        break\n
\n
  category_list.extend(item_list)\n
\n
return category_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Predicate_getMembershipCriterionCategoryList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
