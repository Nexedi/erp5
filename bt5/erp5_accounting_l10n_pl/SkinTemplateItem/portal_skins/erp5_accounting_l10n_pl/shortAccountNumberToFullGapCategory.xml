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
            <value> <string>gap_root = kw.get(\'gap_root\', context.getPortalObject().portal_preferences.getPreferredAccountingTransactionGap())\n
\n
parts=[]\n
for i in range(len(accountNumber)+1):\n
  parts.append(accountNumber[:i])\n
  context.log(parts)\n
return gap_root+\'/\'.join(parts)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>accountNumber, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>shortAccountNumberToFullGapCategory</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
