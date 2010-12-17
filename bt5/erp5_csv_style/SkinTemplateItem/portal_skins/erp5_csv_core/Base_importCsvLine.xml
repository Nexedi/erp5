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
            <value> <string>if object_property_dict[\'uid\'] is None:\n
  object = None\n
else:\n
  object = context.portal_catalog.getObject(object_property_dict[\'uid\'])\n
\n
if object == None:\n
  object = context.newContent()\n
\n
# activity doesn\'t support security rights yet...\n
for key in [\'uid\',\'id\']:\n
  if object_property_dict.has_key(key):\n
    object_property_dict.pop(key)\n
\n
object.edit(**object_property_dict)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>object_property_dict</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_importCsvLine</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
