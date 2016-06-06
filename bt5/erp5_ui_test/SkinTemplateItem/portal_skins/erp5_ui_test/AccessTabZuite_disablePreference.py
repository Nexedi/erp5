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
            <value> <string>"""Disable erp5_ui_test_preference preference"""\n
preference_tool = context.portal_preferences\n
preference = getattr(preference_tool, "access_tab_test_preference", None)\n
if preference is not None:\n
  preference.disable()\n
  # enable the erp5_ui_test_preference again....\n
  erp5_ui_test_preference = getattr(context.portal_preferences, "erp5_ui_test_preference", None)\n
  if erp5_ui_test_preference is not None and \\\n
       erp5_ui_test_preference.getPreferenceState() in (\'draft\', \'disabled\'):\n
    erp5_ui_test_preference.enable()\n
  \n
return \'Disabled Preference Successfully.\'\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccessTabZuite_disablePreference</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Disable preference</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
