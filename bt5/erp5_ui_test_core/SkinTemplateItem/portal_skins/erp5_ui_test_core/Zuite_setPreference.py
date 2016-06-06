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
            <value> <string>"""Set subversion working copy list and enable preference.\n
\n
This script is called by Products.ERP5Type.tests.runFunctionalTest to set\n
subversion working copy paths and conversion server address.\n
It\'s not meant to be called by zelenium tests directly.\n
"""\n
\n
pref = getattr(context.portal_preferences, "erp5_ui_test_preference", None)\n
if pref is None:\n
  pref = context.portal_preferences.newContent(id="erp5_ui_test_preference",\n
                                               portal_type="Preference",\n
                                               priority=1)\n
\n
pref.setPreferredSubversionWorkingCopyList(tuple(working_copy_list.split(\',\')))\n
pref.setPreferredHtmlStyleUnsavedFormWarning(False)\n
\n
if pref.getPreferenceState() == \'disabled\':\n
  pref.enable()\n
\n
pref = getattr(context.portal_preferences, "erp5_ui_test_system_preference", None)\n
if pref is None:\n
  pref = context.portal_preferences.newContent(id="erp5_ui_test_system_preference",\n
                                               portal_type="System Preference",\n
                                               priority=1)\n
\n
pref.setPreferredOoodocServerAddress(conversion_server_hostname)\n
pref.setPreferredOoodocServerPortNumber(conversion_server_port)\n
\n
if pref.getPreferenceState() == \'disabled\':\n
  pref.enable()\n
\n
return \'Set Preference Successfully.\'\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>working_copy_list, conversion_server_hostname, conversion_server_port</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Zuite_setPreference</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Set Test Runner Preferences</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
