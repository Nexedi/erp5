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
            <value> <string># this script allow to create a new object from this current one\n
\n
current_object = context.getObject()\n
module = context.getPortalObject().support_request_module\n
\n
# Create a new object\n
new_id = str(module.generateNewId())\n
context.portal_types.constructContent(type_name=\'Support Request\',\n
        container=module,\n
        id=new_id\n
)\n
new_object = module[new_id]\n
\n
\n
# If we do this before, each added line will take 20 times more time\n
# because of programmable acquisition\n
new_object.edit(\n
        title=current_object.getTitle(),\n
        client_value_list = current_object.getSourceValueList()\n
)\n
# Now create the relation between the current object and the new one\n
current_object.setFollowUpValueList([new_object])\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Event_createSupportRequest</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
