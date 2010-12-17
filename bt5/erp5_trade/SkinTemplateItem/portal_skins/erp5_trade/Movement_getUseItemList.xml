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
            <value> <string>from Products.ERP5Type.Utils import UpperCase\n
\n
portal_categories = context.portal_categories\n
portal_preferences = context.portal_preferences\n
method_id = portal_preferences.getPreference(\'preferred_category_child_item_list_method_id\', \'getCategoryChildCompactLogicalPathItemList\')\n
\n
item_list = getattr(portal_categories.use, method_id)(local_sort_id=(\'int_index\', \'translated_title\'), checked_permission=\'View\')\n
\n
resource = context.getResourceValue()\n
if resource is None:\n
  item_display_list = item_list\n
else:\n
  selected_use_list = [use_value.getCategoryRelativeUrl() for use_value in resource.getUseValueList() + context.getUseValueList()]\n
  item_display_list = [(\'\', \'\')] + [item for item in item_list if item[1] in selected_use_list]\n
\n
return item_display_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Movement_getUseItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
