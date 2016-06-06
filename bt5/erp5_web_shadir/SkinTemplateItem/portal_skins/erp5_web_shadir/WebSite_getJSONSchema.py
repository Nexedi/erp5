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
            <value> <string>return {\n
   \'type\': \'array\',\n
   \'items\': [\n
      {\'type\': \'object\',\n
       \'properties\':{\n
          \'file\':{\n
             \'type\': \'string\',\n
             \'required\': True,\n
          },\n
          \'urlmd5\': {\n
             \'type\': \'string\',\n
             \'required\': True,\n
          },\n
          \'sha512\': {\n
             \'type\': \'string\',\n
             \'required\': True,\n
          },\n
          \'creation_date\': {\n
             \'type\': \'string\',\n
             \'required\': False,\n
          },\n
          \'expiration_date\': {\n
             \'type\': \'string\',\n
             \'required\': False,\n
          },\n
          \'distribution\': {\n
             \'type\': \'string\',\n
             \'required\': False,\n
          },\n
          \'architecture\': {\n
             \'type\': \'string\',\n
             \'required\': False,\n
          },\n
       }\n
     },\n
     {\'type\': \'string\',\n
      \'blank\': True},\n
   ]\n
}\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSite_getJSONSchema</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
