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
            <value> <string>for ti in sorted(context.getPortalObject().portal_types.contentValues(), key=lambda x:x.getId()):\n
  for ai in sorted(ti.contentValues(portal_type=\'Action Information\'), key=lambda x:x.getReference()):\n
    print ti.getId()\n
    print " ", "\\n  ".join([x for x in (\n
      "Reference: %s" % ai.getReference(),\n
      "Title: %s" % ai.getTitle(),\n
      "Action: %s" % ai.getActionText(),\n
      "Icon: %s" % ai.getIconText(),\n
      "Permission: %s" % ai.getActionPermission(),\n
      "Action Type: %s" % ai.getActionType(),\n
      "Visible: %s" % ai.getVisible(),\n
      "Index: %s" % ai.getFloatIndex())])\n
    print\n
\n
return printed\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_dumpPortalTypeActionList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
