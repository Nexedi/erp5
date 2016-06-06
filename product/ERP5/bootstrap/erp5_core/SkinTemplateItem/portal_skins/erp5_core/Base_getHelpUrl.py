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
            <value> <string>if context.REQUEST.has_key(\'workflow_action\'): # We are on a workflow transition\n
  help = \'%s#%s\' % (getattr(getattr(context, form_id), \'form_action\'),context.REQUEST[\'workflow_action\'])\n
elif action is not None:\n
  help = \'%s#%s\' % (context.getPortalTypeName(), action)\n
elif form_id is not None:\n
  help = \'%s_%s\' % (context.getPortalTypeName(), form_id)\n
else:\n
  help = context.getPortalTypeName()\n
return \'%s/%s\' % (context.portal_preferences.getPreferredHtmlStyleDocumentationBaseUrl(), help)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id = None, action = None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getHelpUrl</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
