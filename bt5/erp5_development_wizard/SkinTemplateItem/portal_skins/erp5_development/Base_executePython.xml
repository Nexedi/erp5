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
            <value> <string>selection_id = \'python_shell_selection\'\n
portal = context.getPortalObject()\n
portal_selections = portal.portal_selections\n
\n
if python_expression is None:\n
  python_expression = context.REQUEST.get(\'python_expression\')\n
if python_expression is None:\n
  # take from hard coded selection as when browsing listboxes\n
  # sql_expression is simply not available\n
  selection_object = portal_selections.getSelectionParamsFor(selection_id)\n
  if selection_object:\n
    python_expression = selection_object.get(\'python_expression\')\n
\n
# update selection\n
portal_selections.setSelectionParamsFor(selection_id, \\\n
         dict(python_expression=python_expression))\n
\n
# pass all to code runner\n
return context.Base_runPythonCode(python_expression)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>python_expression=None,**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_executePython</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
