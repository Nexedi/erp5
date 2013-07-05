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

test_list = []\n
\n
test_dict = {\'objective time to view object form\': \'view_object\',\n
             \'time to view object form with many lines\': \'view_100_lines\',\n
             \'time to view proxyfield form\': \'view_proxyfield\',\n
             \'add =\': \'add_%u\',\n
             \'tic =\': \'tic_%u\',\n
             \'view =\': \'view_%u\',\n
             }\n
\n
for result_line in context.objectValues(portal_type=\'Test Result Line\'):\n
  test = {}\n
  object_count = None\n
  for line in result_line.getProperty(\'stdout\').splitlines():\n
    for k, v in test_dict.items():\n
      if k in line:\n
        test[\'%\' in v and v % object_count or v] = \\\n
          float(line.split(\'<\')[1].strip())\n
        break\n
    else:\n
      if line.startswith(\'nb objects =\'):\n
        object_count = int(line.split()[-1])\n
  test_list.append(test)\n
\n
return test_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TestResult_getTestPerfTimingList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
