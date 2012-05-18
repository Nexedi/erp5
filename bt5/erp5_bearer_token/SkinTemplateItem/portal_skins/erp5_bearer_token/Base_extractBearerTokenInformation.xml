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

from DateTime import DateTime\n
try:\n
  token_dict = context.Base_getBearerToken(token)\n
except KeyError:\n
  # not found\n
  return None\n
\n
key = context.getPortalObject().portal_preferences.getPreferredBearerTokenKey()\n
\n
if context.Base_getHMAC(key, str(token_dict)) != token:\n
  # bizzare, not valid\n
  return None\n
\n
if DateTime().timeTime() > token_dict[\'expiration_timestamp\']:\n
  # expired\n
  return None\n
\n
if token_dict[\'user-agent\'] == context.REQUEST.getHeader(\'User-Agent\') and token_dict[\'remote-addr\'] == context.REQUEST.get(\'REMOTE_ADDR\'):\n
  # correct\n
  return token_dict[\'reference\']\n
return None\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>token</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_extractBearerTokenInformation</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
