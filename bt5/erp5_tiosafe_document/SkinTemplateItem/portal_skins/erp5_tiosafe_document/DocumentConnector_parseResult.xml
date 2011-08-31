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
            <value> <string>parser_dict = parser_dict[\'object\'][1]\n
data_list = []\n
for dictionnary in result:\n
  property_dict = {}\n
  for k, v in dictionnary.items():\n
    k = parser_dict.get(k)\n
    if k is not None:\n
      k = k[0]\n
      if same_type(v, ""):\n
        property_dict[k] = unicode(v)\n
      else:\n
        property_dict[k] = v\n
  data_list.append(property_dict)\n
return data_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>result, parser_dict</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>DocumentConnector_parseResult</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
