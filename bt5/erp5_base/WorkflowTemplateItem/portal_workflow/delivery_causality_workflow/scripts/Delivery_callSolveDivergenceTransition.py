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
            <value> <string encoding="cdata"><![CDATA[

from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
\n
delivery = state_change[\'object\']\n
divergence_list =  delivery.getDivergenceList()\n
Base_translateString = delivery.Base_translateString\n
if not len(divergence_list):\n
  delivery.converge()\n
  raise ValidationFailed(Base_translateString(\'No divergence found.\'))\n
\n
delivery_solve_property_dict = {}\n
listbox = state_change[\'kwargs\'].get(\'delivery_group_listbox\')\n
if listbox is not None:\n
  for k, v in listbox.items():\n
    object_url = v[\'choice\']\n
    if object_url != \'ignore\':\n
      object = delivery.restrictedTraverse(object_url)\n
      delivery_solve_property_dict[k] = object.getPropertyList(k)\n
\n
divergence_to_accept_list = []\n
divergence_to_adopt_list = []\n
\n
divergence_dict = {}\n
for divergence in divergence_list:\n
  simulation_movement_url = divergence.getProperty(\'simulation_movement\').getRelativeUrl()\n
  property = divergence.getProperty(\'tested_property\')\n
  divergence_dict[\'%s&%s\' % (simulation_movement_url, property)] = divergence\n
\n
for listbox in [state_change[\'kwargs\'].get(\'line_group_listbox\'),\n
                state_change[\'kwargs\'].get(\'cell_group_listbox\')]:\n
  if listbox is None:\n
    continue\n
  for k, v in listbox.items():\n
    divergence = divergence_dict.get(k, None)\n
    if divergence is None:\n
      raise ValidationFailed(Base_translateString(\'Some divergences seem already solved. Please retry.\'))\n
    choice = v[\'choice\']\n
    if choice == \'accept\':\n
      divergence_to_accept_list.append(divergence)\n
    elif choice == \'adopt\':\n
      divergence_to_adopt_list.append(divergence)\n
\n
delivery.solveDivergence(delivery_solve_property_dict=delivery_solve_property_dict,\n
                         divergence_to_accept_list=divergence_to_accept_list,\n
                         divergence_to_adopt_list=divergence_to_adopt_list,\n
                         comment=\'\')\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Delivery_callSolveDivergenceTransition</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
