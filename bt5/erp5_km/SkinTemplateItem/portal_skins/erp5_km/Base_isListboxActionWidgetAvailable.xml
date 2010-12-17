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
  Determine if listbox action widget can be show or not in context.\n
"""\n
\n
request = context.REQUEST\n
portal = context.getPortalObject()\n
list_mode = request.get(\'list_mode\', False)\n
dialog_mode = request.get(\'dialog_mode\', False)\n
list_style = request.get(\'list_style\', None)\n
context_portal_type = context.getPortalType()\n
\n
if portal.portal_membership.isAnonymousUser() or \\\n
  dialog_mode == True or \\\n
  (list_mode and list_style==\'search\'):\n
  return False\n
\n
# show listbox action widget for module containers only\n
if not context_portal_type.endswith(\'Module\'):# and context_portal_type!=\'Web Site\':\n
  return False\n
\n
return True\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_isListboxActionWidgetAvailable</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
