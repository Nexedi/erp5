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
            <value> <string># This script is intented to be called on a form\n
\n
ps = context.getPortalObject().portal_property_sheets[property_sheet_id]\n
\n
for prop in ps.objectValues(portal_type="Standard Property"):\n
  field_id = "my_%s" %prop.getReference()\n
  if getattr(context, field_id, None) is None:\n
    print "will add %s" %(field_id)\n
    if prop.getElementaryType() == "string":\n
      context.manage_addField(field_id, prop.getReference(), "StringField")\n
    elif prop.getElementaryType() == "boolean":\n
      context.manage_addField(field_id, prop.getReference(), "CheckBoxField")\n
    else:\n
      print "unkown type", prop.getElementaryType()\n
\n
return printed\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>property_sheet_id</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>IntegrationTestModule_createFormFromPropertySheet</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
