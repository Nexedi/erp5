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
            <value> <string>translateString = context.Base_translateString\n
\n
request=context.REQUEST\n
\n
if context.portal_membership.isAnonymousUser() and not captcha_ok:\n
  absolute_url = context.absolute_url()\n
  new_url = \'captcha/CheckCaptcha/view?portal_type=%s\' % new_application_procedure\n
  redirect_url = "%s/%s" % (absolute_url, new_url)\n
else:\n
  portal_type = new_application_procedure\n
  if portal_type is not None and portal_type != \'\':\n
    module = context.getDefaultModule(portal_type=portal_type)\n
    # Create a new procedure\n
    new_procedure = module.newContent(portal_type=portal_type)\n
    absolute_url = context.absolute_url()\n
    module_id = module.getId()\n
    new_object_id = new_procedure.getId()\n
    redirect_url = "%s/%s/%s/%s" % (absolute_url, module_id, new_object_id, \'view\')\n
  else:\n
    message = translateString("You must choose a procedure")\n
\n
    redirect_url = "%s?portal_status_message=%s" % (context.absolute_url(), message)\n
    \n
result = request[\'RESPONSE\'].redirect(redirect_url) \n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>new_application_procedure, captcha_ok=False</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>EGov_createNewProcedure</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
