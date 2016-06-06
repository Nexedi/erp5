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
for path in path_list:\n
  document = portal.restrictedTraverse(path)\n
  # Useful to reproduce Ingestion process from beginning\n
  # All properties of object are considered as user input\n
  input_parameter_dict = {\'portal_type\': document.getPortalType()}\n
  for property_id in document.propertyIds():\n
    if property_id not in (\'portal_type\', \'uid\', \'id\',) \\\n
      and document.hasProperty(property_id):\n
      input_parameter_dict[property_id] = document.getProperty(property_id)\n
  filename = document.getFilename()\n
\n
  # Now starts metadata discovery process\n
  document.activate().discoverMetadata(filename=filename, input_parameter_dict=input_parameter_dict)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>path_list</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Alarm_processIngestedWebMessageList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
