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
            <value> <string>from zExceptions import Unauthorized\n
if REQUEST is not None:\n
  raise Unauthorized\n
\n
result = None\n
access_token_document = context\n
request = context.REQUEST\n
\n
if access_token_document.getValidationState() == \'validated\':\n
  comment = "Token invalidated but non correctly authentificated"\n
\n
  if (request["REQUEST_METHOD"] == access_token_document.getUrlMethod()) and \\\n
    (request["ACTUAL_URL"] == access_token_document.getUrlString()):\n
\n
    agent_document = access_token_document.getAgentValue()\n
    if agent_document is not None:\n
      result = agent_document.getReference(None)\n
      comment = "Token usage accepted"\n
\n
  access_token_document.invalidate(comment=comment)\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>REQUEST=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>OneTimeRestrictedAccessToken_getExternalLogin</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
