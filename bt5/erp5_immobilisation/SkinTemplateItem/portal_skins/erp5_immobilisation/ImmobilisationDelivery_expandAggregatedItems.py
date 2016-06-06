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
            <value> <string>item_list = []\n
movement_list = context.getImmobilisationMovementList()\n
#context.log(\'movement_list %s\' % context.getRelativeUrl(),[m.getPath() for m in movement_list])\n
movemement_path_list = []\n
for movement in movement_list:\n
  movemement_path_list.append(movement.getPath())\n
  for item in movement.getAggregateValueList():\n
    if item not in item_list:\n
      item_list.append(item)\n
for item in item_list:\n
  item.activate(tag=\'expand_amortisation\', after_path_and_method_id=(movemement_path_list, (\'immediateReindexObject\', \'recursiveImmediateReindexObject\', \'updateImmobilisationState\',) )).expandAmortisation()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ImmobilisationDelivery_expandAggregatedItems</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
