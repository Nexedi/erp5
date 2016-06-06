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
            <value> <string>"""Unlink simulation movements when delivery movement is deleted.\n
This way when a delivery movement is deleted, corresponding simulation movement\n
will again be candidates for building in another delivery.\n
\n
XXX: security (future) bug: this requires that the system is configured in a way where \n
simulation movement can be accessed in restrictred mode. For now this script has a proxy\n
role, but someday we\'ll have to move this to unrestricted environment.\n
"""\n
delivery_movement = state_change[\'object\']\n
\n
# Always modify movement even if there is no related movement simulation,\n
# because a concurrent transaction may be linking one to this movement\n
# (which would modify the local index for "delivery" category).\n
# In such case, one of the 2 transactions must be restarted.\n
delivery_movement.serialize()\n
\n
# Clean simulation\n
simulation_movement_list = delivery_movement.getDeliveryRelatedValueList(\n
    portal_type="Simulation Movement")\n
for simulation_movement in simulation_movement_list:\n
  if simulation_movement.getDelivery() == delivery_movement.getRelativeUrl():\n
    simulation_movement.setDelivery(None)\n
  # \'order\' category is deprecated. it is kept for compatibility.\n
  if simulation_movement.getOrder() == delivery_movement.getRelativeUrl():\n
    simulation_movement.setOrder(None)\n
\n
context.DeliveryMovement_updateSimulation(state_change)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>DeliveryMovement_unlinkSimulation</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
