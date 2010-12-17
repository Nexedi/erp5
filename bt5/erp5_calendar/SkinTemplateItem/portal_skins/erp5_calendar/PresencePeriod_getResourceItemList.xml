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
            <value> <string>portal = context.getPortalObject()\n
\n
preferred_presence_calendar_period_type = portal.portal_preferences\\\n
        .getPreferredPresenceCalendarPeriodType()\n
\n
method_id = portal.portal_preferences.getPreference(\n
     \'preferred_category_child_item_list_method_id\', \'getCategoryChildCompactLogicalPathItemList\')\n
\n
category = portal.portal_categories.calendar_period_type\n
\n
if preferred_presence_calendar_period_type:\n
  category = category.restrictedTraverse(preferred_presence_calendar_period_type, category)\n
\n
return getattr(category, method_id)(local_sort_id=(\'int_index\', \'translated_title\'),\n
                                    checked_permission=\'View\',\n
                                    is_self_excluded=0,\n
                                    base=1)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PresencePeriod_getResourceItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
