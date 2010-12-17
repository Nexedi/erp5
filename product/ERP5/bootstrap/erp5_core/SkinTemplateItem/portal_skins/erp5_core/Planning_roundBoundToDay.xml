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
            <value> <string encoding="cdata"><![CDATA[

"""\n
Script used by PlanningBox validator to round the bound dates to the\n
closest full day.\n
"""\n
if full_date.hour() > 12: \n
  return DateTime(full_date.Date()) + 1\n
else:\n
  return DateTime(full_date.Date())\n
\n
#if axis == \'end\':\n
#    # round to 23:59:59\n
#    if full_date.hour() > 12:\n
#      return DateTime(full_date.Date()) + 1  - (1.0/(24*3600))\n
#    else:\n
#      return DateTime(full_date.Date())  - (1.0/(24*3600))\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>full_date, axis=\'begin\'</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Planning_roundBoundToDay</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
