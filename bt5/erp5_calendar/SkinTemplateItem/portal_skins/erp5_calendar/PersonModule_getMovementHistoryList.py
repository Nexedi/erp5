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
selection_name = \'person_module_selection\'\n
person_list = portal.portal_selections.getSelectionCheckedValueList(selection_name)\n
if not person_list:\n
  person_list = portal.portal_selections.callSelectionFor(selection_name)\n
\n
# Select only the visible part\n
main_axis_begin = context.REQUEST.get(\'list_start\', 0)\n
form = getattr(context, \'PersonModule_viewPlanning\')\n
planning_box = form.get_field(\'planning_box\')\n
main_axis_end = main_axis_begin + planning_box.get_value(\'main_axis_groups\')\n
\n
node_uid_list = [x.uid for x in person_list[main_axis_begin:main_axis_end]]\n
\n
acceptable_state_list = context.getPortalFutureInventoryStateList() + \\\n
                        context.getPortalReservedInventoryStateList() + \\\n
                        context.getPortalTransitInventoryStateList() + \\\n
                        context.getPortalCurrentInventoryStateList()\n
\n
movement_list = context.portal_simulation.getMovementHistoryList(\n
                   node_uid=node_uid_list,\n
                   portal_type=portal_type,\n
                   simulation_state=acceptable_state_list, \n
                   to_date=to_date, \n
                   from_date=from_date,\n
                   omit_mirror_date=0,\n
)\n
\n
\n
# XXX It is a bad idea to return order_value or delivery_value,\n
# because same object can be displayed multiple time in some cases\n
\n
return_list = []\n
\n
# Normally, simulation movement should only have 1 order value\n
for mvt_obj in movement_list:\n
  # XXX Can\'t we use a brain instead ?\n
  if mvt_obj.portal_type == "Simulation Movement":\n
    obj = mvt_obj.getOrderValue()  \n
    if obj is not None:\n
      mvt_obj = obj\n
  return_list.append(mvt_obj)\n
\n
return return_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>to_date=None, from_date=None, portal_type=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PersonModule_getMovementHistoryList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
