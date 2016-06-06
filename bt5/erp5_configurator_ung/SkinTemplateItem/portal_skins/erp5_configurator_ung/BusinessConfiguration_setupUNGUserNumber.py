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

configuration_save_url = kw.get(\'configuration_save_url\', None)\n
user_number = kw.get(\'user_number\', 1)\n
next_transition = context.getNextTransition().getRelativeUrl()\n
\n
if user_number > 1:\n
  # mark next transition  as multiple\n
  context.setMultiEntryTransition(next_transition, user_number)\n
else:\n
  # explicitly reset next transition as not multiple because \n
  # we may have already set it as multiple\n
  context.setMultiEntryTransition(next_transition, 0)\n
\n
# store globally\n
context.setGlobalConfigurationAttr(user_number=user_number)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BusinessConfiguration_setupUNGUserNumber</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Setup number of users</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
