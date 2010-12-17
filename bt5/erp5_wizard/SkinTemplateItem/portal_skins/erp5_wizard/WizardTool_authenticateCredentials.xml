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
            <value> <string># call remote instance to make the real check for us at server side\n
if login is not None and password is not None:\n
  try:\n
    return context.portal_wizard.callRemoteProxyMethod(\n
                       \'Base_authenticateCredentialsFromExpressInstance\', \\\n
                       use_cache = 0, \\\n
                       ignore_exceptions = 0, \\\n
                       **{\'login\': login,\n
                          \'password\': password,\n
                          \'erp5_uid\': context.ERP5Site_getExpressInstanceUid()})\n
  except:\n
    # if an exception occurs at server side do NOT let user in.\n
    return 0\n
return 0\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>login, password, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WizardTool_authenticateCredentials</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Authenticate against Authentification Server</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
