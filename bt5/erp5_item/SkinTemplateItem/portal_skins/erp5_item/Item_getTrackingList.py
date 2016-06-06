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
            <value> <string>from Products.ERP5Type.Document import newTempBase\n
portal = context.getPortalObject()\n
catalog = portal.portal_catalog.getResultValue\n
if current:\n
  method = portal.portal_simulation.getCurrentTrackingList\n
else:\n
  method = portal.portal_simulation.getTrackingList\n
\n
uid = context.getUid()\n
\n
history_list = []\n
\n
simulation_state = portal.getPortalCurrentInventoryStateList() \\\n
                                  + portal.getPortalTransitInventoryStateList() \\\n
                                  + portal.getPortalReservedInventoryStateList()\n
\n
kw[\'item.simulation_state\'] = simulation_state\n
for res in method(aggregate_uid=uid, **kw):\n
  history = newTempBase(context, str(len(history_list)))\n
  explanation = catalog(uid=res.delivery_uid)\n
  node_value = catalog(uid=res.node_uid)\n
  section_value = catalog(uid=res.section_uid)\n
  resource_value = catalog(uid=res.resource_uid) \n
  history.edit(\n
      #uid = catalog(uid=res.uid).getTitle(),\n
      date=res.getDate(),\n
      node_title=node_value is not None and node_value.getTitle() or None,\n
      source_title=explanation.getSourceTitle(),\n
      section_title=section_value is not None and section_value.getTitle() or None,\n
      resource_title=resource_value is not None and resource_value.getTitle() or None,\n
      explanation=explanation.getTitle(),\n
      translated_portal_type = explanation.getTranslatedPortalType(),\n
      quantity = explanation.getQuantity(),\n
      url=explanation.absolute_url(),\n
      item_quantity = context.getQuantity(at_date=res.getDate()), \n
      variation_category_item_list = [x[0] for x in explanation.getVariationCategoryItemList()],\n
      simulation_state=explanation.getTranslatedSimulationStateTitle(),\n
  )\n
 \n
  history_list.append(history)\n
  \n
return history_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>current=0, *args, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Item_getTrackingList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
