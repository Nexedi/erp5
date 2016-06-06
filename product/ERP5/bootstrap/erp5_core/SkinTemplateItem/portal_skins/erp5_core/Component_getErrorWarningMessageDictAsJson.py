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

import re\n
message_re = re.compile(r\'[CRWEF]:\\s*(?P<line>\\d+),\\s*(?P<column>\\d+):\\s*.*\')\n
\n
def getParsedMessageList(message_list):\n
  result_list = []\n
  for message in message_list:\n
    line = None\n
    column = None\n
    message_obj = message_re.match(message)\n
    if message_obj:\n
      line = int(message_obj.group(\'line\'))\n
      column = int(message_obj.group(\'column\'))\n
\n
    result_list.append({\'line\': line, \'column\': column, \'message\': message})\n
\n
  return result_list\n
\n
import json\n
return json.dumps({\'error_list\': getParsedMessageList(context.getTextContentErrorMessageList()),\n
                   \'warning_list\': getParsedMessageList(context.getTextContentWarningMessageList())})\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Component_getErrorWarningMessageDictAsJson</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
