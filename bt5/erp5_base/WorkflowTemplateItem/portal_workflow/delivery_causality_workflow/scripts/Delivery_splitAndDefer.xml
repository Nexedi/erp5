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
            <value> <string>delivery = state_change[\'object\']\n
\n
split_movement_list = state_change[\'kwargs\'][\'split_movement_list\']\n
start_date = state_change[\'kwargs\'][\'start_date\']\n
stop_date = state_change[\'kwargs\'][\'stop_date\']\n
\n
if not len(split_movement_list):\n
  delivery.updateCausalityState()\n
  return\n
\n
tag = delivery.getPath() + \'_split\'\n
\n
for movement in split_movement_list:\n
  delivery.getPortalObject().portal_simulation.solveMovement(\n
    movement, None, \'SplitAndDefer\', start_date=start_date,\n
    stop_date=stop_date, activate_kw={\'tag\':tag})\n
\n
delivery.activate(after_tag=tag).updateCausalityState()\n
\n
# Create delivery\n
explanation_uid_list = []\n
object = delivery\n
while object is not None:\n
  explanation_uid_list.append(object.getUid())\n
  object = object.getCausalityValue()\n
    \n
previous_tag = None\n
for delivery_builder in delivery.getBuilderList():\n
  this_builder_tag = \'%s_split_%s\' % (delivery.getPath(),\n
                                      delivery_builder.getId())\n
  after_tag = [tag]\n
  if previous_tag:\n
    after_tag.append(previous_tag)\n
  delivery_builder.activate(activity=\'SQLQueue\',\n
                            tag=this_builder_tag,\n
                            after_tag=after_tag).build(\n
                                  explanation_uid=explanation_uid_list)\n
  previous_tag = this_builder_tag\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Delivery_splitAndDefer</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
