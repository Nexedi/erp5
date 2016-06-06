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
            <value> <string>default_method_name = \'getCategoryChildTranslatedCompactLogicalPathItemList\'\n
method_name = context.portal_preferences.getPreference(\'preferred_category_child_item_list_method_id\', default=default_method_name)\n
\n
if not translate:\n
  method_name = method_name.replace(\'Translated\', \'\')\n
\n
if translate:\n
  if \'Compact\' in method_name:\n
    local_sort_id_list = (\'int_index\', \'translated_short_title\')\n
  else:\n
    local_sort_id_list = (\'int_index\', \'translated_title\')\n
else:\n
  if \'Compact\' in method_name:\n
    local_sort_id_list = (\'int_index\', \'short_title\')\n
  else:\n
    local_sort_id_list = (\'int_index\', \'title\')\n
\n
method = getattr(base_category, method_name)\n
\n
return method(local_sort_id=local_sort_id_list, checked_permission=\'View\', **kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>base_category, translate=True, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getPreferredCategoryChildItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
