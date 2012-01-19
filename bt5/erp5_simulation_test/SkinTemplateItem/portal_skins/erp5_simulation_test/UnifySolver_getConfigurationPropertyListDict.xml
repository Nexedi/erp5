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
This script returns a dictionary of possible values for Unify Solver.\n
"""\n
solver_decision = context.getCausalityValue()\n
tester = solver_decision.getCausalityValue()\n
value_list_dict = {}\n
for property_id in tester.getTestedPropertyList():\n
  value_list = []\n
  for simulation_movement in context.getDeliveryValueList():\n
    movement = simulation_movement.getDeliveryValue()\n
    value = movement.getProperty(property_id)\n
    if value not in value_list:\n
      value_list.append(value)\n
    simulation_movement_list = movement.getDeliveryRelatedValueList()\n
    value = simulation_movement.getProperty(property_id)\n
    if value not in value_list:\n
      value_list.append(value)\n
  value_list_dict[property_id] = [(x, str(x)) for x in value_list]\n
return value_list_dict\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>UnifySolver_getConfigurationPropertyListDict</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
