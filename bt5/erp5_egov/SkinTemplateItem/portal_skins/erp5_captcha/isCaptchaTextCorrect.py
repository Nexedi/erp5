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
session_id = request.get(\'erp5_captcha_session_id\', None)\n
if session_id is None:\n
  return \'no session\'\n
# get session\n
session = context.portal_sessions[session_id]\n
\n
if session.has_key(\'captcha_text\') and  session.has_key(\'captcha_image_path\'):\n
  captcha_text = session[\'captcha_text\']\n
  captcha_file_path = session[\'captcha_image_path\']\n
\n
if text_to_check == captcha_text:\n
  return True\n
\n
return False\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>text_to_check</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>isCaptchaTextCorrect</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
