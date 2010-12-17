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
            <value> <string>"""\n
  Translates a short account number (eg 280) to a full gap category url (eg gap/2/28/280).\n
"""\n
\n
number = gap_id.strip()\n
\n
gap_url = gap_base\n
for i in range(len(number)):\n
  gap_url += number[:i+1] + \'/\'\n
\n
return gap_url[:-1]\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>gap_id, gap_base=\'gap/fr/pcg/\'</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>GAPCategory_getURLFromId</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
