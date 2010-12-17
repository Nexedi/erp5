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
            <value> <string>from DateTime import DateTime\n
def sorted(seq):\n
  seq = seq[:]\n
  seq.sort()\n
  return seq\n
\n
portal = context.getPortalObject()\n
request = portal.REQUEST\n
\n
if not at_date:\n
  at_date=DateTime()\n
\n
brain = context\n
\n
tracking_parameters = dict(\n
    node_uid=brain.node_uid,\n
    resource_uid=brain.resource_uid,\n
    at_date=at_date,\n
    )\n
\n
result_list = []\n
\n
if context.getVariationCategoryList():\n
  tracking_parameters[\'variation_text\'] = brain.variation_text\n
\n
\n
for tracking_brain in portal.portal_simulation.getCurrentTrackingList(\n
                            **tracking_parameters):\n
  item = tracking_brain.getObject()\n
 \n
  item_dict = "%s : %s"% ( item.getReference(),\n
                           item.getQuantity(at_date=at_date) )\n
  result_list.append(item_dict)\n
\n
return sorted(result_list)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>at_date=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Inventory_getAggregatedItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
