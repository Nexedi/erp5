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
translateString = portal.Base_translateString\n
\n
property_sheet_value_list = context.getRecursivePropertySheetValueList()\n
if not len(property_sheet_value_list):\n
  return context.Base_redirect(\n
    \'view\',\n
    keep_items={\'portal_status_message\':\n
                translateString(\'No ${portal_type} related.\',\n
                                mapping={\'portal_type\': \'Property Sheet\'})})\n
\n
elif len(property_sheet_value_list) == 1:\n
  property_sheet = property_sheet_value_list[0]\n
  return property_sheet.Base_redirect(\n
    \'view\',\n
    keep_items={\'portal_status_message\':\n
                translateString(\'${this_portal_type} related to ${that_portal_type}: ${that_title}.\',\n
                                mapping={\'this_portal_type\': \'Property Sheet\',\n
                                \'that_portal_type\': context.getPortalType(),\n
                                \'that_title\': context.getTitleOrId()})})\n
\n
property_sheet_uid_list = [property_sheet.getUid()\n
                           for property_sheet in property_sheet_value_list]\n
\n
return portal.portal_property_sheets.Base_redirect(\n
  \'view\',\n
  keep_items={\'reset\': 1,\n
              \'ignore_hide_rows\': 1,\n
              \'uid\': property_sheet_uid_list})\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BaseType_jumpToPropertySheetList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
