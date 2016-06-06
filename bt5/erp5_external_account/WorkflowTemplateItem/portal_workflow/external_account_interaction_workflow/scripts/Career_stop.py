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
  Stop respective account for a company employee.\n
"""\n
portal = context.getPortalObject()\n
\n
career = state_change[\'object\']\n
person = career.getParentValue()\n
\n
default_email_text = person.Person_getDefaultExternalEmailText()\n
username, domain = default_email_text.split(\'@\', 2)\n
if domain in portal.portal_preferences.getPreferredManagedExternalDomainNameList():\n
  # find external Email Account instance and invalidate it\n
  kw = {\'email.url_string\': default_email_text,\n
        \'default_source_uid\': person.getUid(),\n
        \'portal_type\': \'Email Account\',\n
        \'validation_state\': \'validated\'}\n
  email_account = portal.portal_catalog.getResultValue(**kw)\n
  if email_account is not None:\n
    email_account.invalidate()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Career_stop</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
