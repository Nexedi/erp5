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
  Get session data\n
"""\n
\n
request = context.REQUEST\n
now = DateTime()\n
expire_timeout_days = 90\n
session_id = request.get(\'session_id\', None)\n
if session_id is None:\n
  ## first call so generate session_id and send back via cookie\n
  session_id = \'erp5runmydocs_\' + context.REQUEST.other[\'AUTHENTICATED_USER\'].getUserName()\n
  request.RESPONSE.setCookie(\'erp5_session_id\', \n
                             session_id, \n
                             expires=(now +expire_timeout_days).fCommon(), path=\'/\')\n
\n
if attribute is None or not attribute:\n
  return context.portal_sessions[session_id]\n
else:\n
  return context.portal_sessions[session_id][attribute]\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>attribute = \'\'</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5RunMyDocs_acquireSession</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
