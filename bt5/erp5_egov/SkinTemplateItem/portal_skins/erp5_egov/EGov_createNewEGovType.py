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
            <value> <string>request=context.REQUEST\n
\n
if context.portal_membership.isAnonymousUser() and not captcha_ok:\n
  absolute_url = context.absolute_url()\n
  new_url = \'captcha/CheckCaptcha/view\'\n
  redirect_url = "%s/%s" % (absolute_url, new_url)\n
else:\n
  \n
  portal_types = context.getPortalObject().portal_types\n
  # Create a new procedure\n
  new_procedure = portal_types.newContent(portal_type=\'EGov Type\')\n
  absolute_url = portal_types.absolute_url()\n
  new_object_id = new_procedure.getId()\n
\n
  redirect_url = "%s/%s/%s" % (absolute_url, new_object_id, \'view\')\n
\n
result = request[\'RESPONSE\'].redirect(redirect_url) \n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>captcha_ok=False</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>EGov_createNewEGovType</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
