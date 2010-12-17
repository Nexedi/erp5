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
\n
resource_portal_type = "Product"\n
node_portal_type = "Organisation"\n
site_portal_type = "Category"\n
\n
order_portal_type = "Sale Order"\n
delivery_portal_type = "Sale Packing List"\n
\n
resource_id = "erp5_pdm_ui_test_product"\n
\n
source_node_id = "erp5_pdm_ui_test_source_node"\n
destination_node_id = "erp5_pdm_ui_test_destination_node"\n
\n
source_site_id = "erp5_pdm_ui_test_source_site"\n
destination_site_id = "erp5_pdm_ui_test_destination_site"\n
\n
delivery_id = "erp5_pdm_ui_test_delivery"\n
\n
# Delete resource\n
module = portal.getDefaultModule(resource_portal_type)\n
if getattr(module, resource_id, None) is not None:\n
  module.manage_delObjects([resource_id])\n
\n
# Delete nodes\n
module = portal.getDefaultModule(node_portal_type)\n
for node_id in (source_node_id, destination_node_id):\n
  if getattr(module, node_id, None) is not None:\n
    module.manage_delObjects([node_id])\n
\n
# Delete categories\n
base_category = portal.restrictedTraverse(\'portal_categories/site\')\n
for site_id in (source_site_id, destination_site_id):\n
  if getattr(base_category, site_id, None) is not None:\n
    base_category.manage_delObjects([site_id])\n
\n
stool = portal.portal_simulation\n
# Delete order\n
module = portal.getDefaultModule(order_portal_type)\n
if getattr(module, delivery_id, None) is not None:\n
  delivery = getattr(module, delivery_id)\n
  stool.manage_delObjects(delivery.getCausalityRelatedIdList(portal_type=\'Applied Rule\'))\n
  module.manage_delObjects([delivery_id])\n
\n
# Delete delivery\n
module = portal.getDefaultModule(delivery_portal_type)\n
if getattr(module, delivery_id, None) is not None:\n
  delivery = getattr(module, delivery_id)\n
  stool.manage_delObjects(delivery.getCausalityRelatedIdList(portal_type=\'Applied Rule\'))\n
  module.manage_delObjects([delivery_id])\n
\n
return "Deleted Successfully."\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PdmZuite_deleteData</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
