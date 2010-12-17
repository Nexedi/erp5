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
  Use this function in local TioLive instance form to change global password for an user.\n
"""\n
\n
portal = context.getPortalObject()\n
kw = {\'reference\': reference,\n
      \'new_password\': new_password,\n
      \'old_password\': old_password,\n
      \'erp5_uid\': portal.ERP5Site_getExpressInstanceUid()}\n
return portal.portal_wizard.callRemoteProxyMethod( \\\n
                              distant_method = \'WitchTool_changeGlobalUserPasswordFromExpressInstance\', \\\n
                              use_cache = 0, \\\n
                              ignore_exceptions = 0, \\\n
                              **kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>reference, old_password, new_password</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WizardTool_changeGlobalUserPasswordFromExpressInstance</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
