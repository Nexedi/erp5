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
            <value> <string>sub = context.restrictedTraverse(context_document)\n
while sub.getParentValue().getPortalType() !=  "Synchronization Tool":\n
  sub = sub.getParentValue()\n
\n
im = sub.Base_getRelatedObjectList(portal_type=\'Integration Module\')[0].getObject()\n
org_module = im.getParentValue().organisation_module\n
org_pub = org_module.getSourceSectionValue()\n
gid = org_pub.getGidFromObject(context.getSubordinationValue(), encoded=False)\n
\n
return str(gid)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>context_document</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Node_getRelation</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
