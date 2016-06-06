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

result_list = []\n
for brain in context.portal_simulation.getCurrentInventoryList(\n
    node_category=node_category,\n
    section_category=section_category,\n
    group_by_resource=True,\n
    group_by_variation=True,\n
    group_by_node=False,\n
    at_date=at_date,\n
    # resource_portal_type= does not work with cells (because resource is acquired from line)\n
    resourceType=context.getPortalProductTypeList(),\n
    **kw):\n
\n
  if positive_stock and negative_stock and not zero_stock and brain.inventory == 0:\n
     result_list.append(brain)\n
  if positive_stock and not negative_stock and zero_stock and brain.inventory <0:\n
     result_list.append(brain)\n
  if negative_stock and zero_stock and not positive_stock and brain.inventory >0:\n
     result_list.append(brain)\n
  if positive_stock and not negative_stock and not zero_stock and brain.inventory <=0:\n
     result_list.append(brain)\n
  if negative_stock and not positive_stock and not zero_stock and brain.inventory >=0:\n
     result_list.append(brain)\n
  if zero_stock and not positive_stock and not negative_stock and brain.inventory!=0:\n
     result_list.append(brain)\n
  if not positive_stock and not negative_stock and not zero_stock:\n
     result_list.append(brain)\n
\n
return sorted(result_list, key=lambda brain: (brain.getResourceReference(), brain.getResourceTitle(), brain.variation_text))\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>at_date=None, node_category=None, section_category=None, positive_stock=None, negative_stock=None, zero_stock=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getBySiteCurrentStockList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
