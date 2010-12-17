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
  This script resets security on all forms after validation by registry officer\n
"""\n
\n
portal = context.getPortalObject()\n
request_eform = state_change[\'object\']\n
N_ = portal.Base_translateString\n
\n
new_reference = request_eform.getRegistrationNumber()\n
\n
sql_kw = {}\n
sql_kw[\'portal_type\'] = \'Assignment\'\n
sql_kw[\'validation_state\'] = \'open\'\n
sql_kw[\'default_destination_uid\'] = request_eform.getUid()\n
sql_kw[\'default_function_uid\'] = request_eform.portal_categories.function.entreprise.getUid()\n
for assignment in request_eform.portal_catalog(**sql_kw):\n
  assignment.setCorporateRegistrationCode(new_reference)\n
\n
# We need to update security now\n
request_eform.updateLocalRolesOnSecurityGroups()\n
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
            <value> <string>resetSecurityOnForms</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
