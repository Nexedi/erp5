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
            <value> <string>\'\'\'\n
  Return a list of user documents corresponding to the title\n
\'\'\'\n
\n
\n
user_corresponding_document_list = []\n
\n
# here we must search in the user digital safe documents that have the given title\n
#XXX to be done\n
\n
if not len(user_corresponding_document_list):\n
  user_corresponding_document_list.append(\'Your digital safe contains no relevant document\')\n
else:\n
  user_corresponding_document_list.append(\'Other\')\n
\n
return user_corresponding_document_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>title=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>EGov_getAttachmentListFromDigitalSafe</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
