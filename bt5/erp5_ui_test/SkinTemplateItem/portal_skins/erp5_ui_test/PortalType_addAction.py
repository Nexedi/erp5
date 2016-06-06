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
            <value> <string>"""Add or replace an action on a type informations from types tool.\n
"""\n
assert context.meta_type in (\'ERP5 Type Information\', \'ERP5 Base Type\'), context.meta_type\n
\n
context.PortalType_deleteAction(id=id)\n
\n
context.addAction( id         = id\n
                 , action     = action\n
                 , name       = name\n
                 , condition  = condition\n
                 , permission = permission\n
                 , category   = category\n
                 , icon       = icon\n
                 , priority   = 10.0\n
                 )\n
\n
return \'Set Successfully.\'\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>name=None, id=None, action=None, icon=None, condition=None, permission=\'View\', category=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PortalType_addAction</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
