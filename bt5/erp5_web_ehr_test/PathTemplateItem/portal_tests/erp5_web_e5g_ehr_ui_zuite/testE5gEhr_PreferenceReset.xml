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
            <value> <string>"""Reset everything for the test"""\n
\n
pref = getattr(context.portal_preferences, "erp5_ui_test_preference", None)\n
if pref is None:\n
  pref = context.portal_preferences.newContent(id="erp5_ui_test_preference", portal_type="Preference")\n
pref.setPreferredListboxViewModeLineCount(None)\n
pref.setPreferredListboxListModeLineCount(10)\n
if pref.getPreferenceState() == \'disabled\':\n
  pref.enable()\n
else:\n
  context.portal_caches.clearAllCache()\n
\n
return \'Reset Successfully.\'\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>testE5gEhr_PreferenceReset</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Reset Everything</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
