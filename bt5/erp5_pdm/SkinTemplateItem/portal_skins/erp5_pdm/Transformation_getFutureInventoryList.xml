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
  Returns the future inventory list of all the Transformed Resources.\n
"""\n
def getTransformationResourceList():\n
  resource_dict = {}\n
  for m in context.contentValues(\n
     filter={\'portal_type\': [\'Transformation Optional Resource\', \'Transformation Transformed Resource\']}):\n
    r = m.getResource()\n
    if r is not None:\n
      resource_dict[r] = 1\n
  return resource_dict.keys()\n
\n
resource_list = getTransformationResourceList()\n
if not resource_list:\n
  # When there is no resource, we have nothing to do.\n
  return []\n
portal = context.getPortalObject()\n
simulation_tool = portal.portal_simulation\n
kw[\'resource\'] = resource_list\n
return simulation_tool.getFutureInventoryList(**kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Transformation_getFutureInventoryList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
