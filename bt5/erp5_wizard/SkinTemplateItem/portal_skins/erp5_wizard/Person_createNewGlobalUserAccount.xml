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
            <value> <string>portal = context.getPortalObject()\n
\n
if person is None:\n
  person = context\n
\n
kw = context.Person_getDataDict(person=person)\n
kw[\'password\'] = password\n
\n
# explicitly check if username is unique\n
if portal.Base_validatePersonReference(kw[\'reference\'], context.REQUEST):\n
  # create user in Authentification Server\n
  kw[\'start_assignment\'] = len(person.Person_getAvailableAssignmentValueList())\n
  portal.portal_wizard.callRemoteProxyMethod(\n
                         \'WitchTool_createNewGlobalUserAccountFromExpressInstance\', \\\n
                         use_cache = 0, \\\n
                         ignore_exceptions = 0, \\\n
                         **kw)\n
else:\n
  # user reference is NOT unique (valid) in Nexedi ERP5\n
  raise ValueError, "User reference not unique"\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>password=None, person=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Person_createNewGlobalUserAccount</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
