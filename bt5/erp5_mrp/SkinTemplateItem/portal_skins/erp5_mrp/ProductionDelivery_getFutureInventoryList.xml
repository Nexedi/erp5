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
            <value> <string>"""List Method script to show only inventory for destination"""\n
\n
# When the delivery does not have a resource, returns empty list.\n
# Otherwise it returns all the inventories in your ERP5 site.\n
production_delivery = context\n
movement_list = production_delivery.getMovementList()\n
empty = True\n
for movement in movement_list:\n
  if movement.getResource() not in (None, \'\'):\n
    empty = False\n
    break           \n
if empty:\n
  return []\n
\n
portal_type_dict_mapping = {\n
  \'Production Order\' : {\'node_uid\' : context.getDestinationUid()},\n
}\n
kw = {}\n
kw[\'group_by_node\'] = 1\n
kw[\'group_by_section\'] = 0\n
kw[\'group_by_variation\'] = 1\n
\n
kw.update( **portal_type_dict_mapping.get(context.getPortalType(),{}) )\n
return context.getFutureInventoryList(*args,**kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*args, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ProductionDelivery_getFutureInventoryList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
