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
            <value> <string>request = context.REQUEST\n
now = DateTime()\n
expire_timeout_days = 1\n
session_id = request.get(\'session_id\', None)\n
if session_id is None or not session_id.startswith("erp5zuite"):\n
  ## first call so generate session_id and send back via cookie\n
  session_id = \'erp5zuite_\' + context.REQUEST.other[\'AUTHENTICATED_USER\'].getUserName()\n
  request.RESPONSE.setCookie(\'erp5_session_id\', session_id, expires=(now +expire_timeout_days).fCommon(), path=\'/\')\n
  \n
session = context.portal_sessions[session_id]\n
if not session.has_key(\'tempfolder\') or session[\'tempfolder\'] == \'\':\n
  session[\'tempfolder\'] = context.Zuite_createTempFolder() + \'/\'\n
\n
return session[\'tempfolder\'] + str(context.portal_ids.generateNewId(id_generator=\'zuite\', id_group=context.getId(), default=1)) + \'.png\'\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Zuite_generateFilename</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
