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
self = context\n
\n
resource_portal_type = "Product"\n
node_portal_type = "Organisation"\n
site_portal_type = "Category"\n
resource_id = "erp5_pdm_ui_test_product"\n
resource_title = "erp5_pdm_ui_test_product_title"\n
source_node_id = "erp5_pdm_ui_test_source_node"\n
source_node_title = "erp5_pdm_ui_test_source_node_title"\n
destination_node_id = "erp5_pdm_ui_test_destination_node"\n
destination_node_title = "erp5_pdm_ui_test_destination_node_title"\n
source_site_id = "erp5_pdm_ui_test_source_site"\n
source_site_title = "erp5_pdm_ui_test_source_site_title"\n
destination_site_id = "erp5_pdm_ui_test_destination_site"\n
destination_site_title = "erp5_pdm_ui_test_destination_site_title"\n
\n
# validate rules\n
for rule in portal.portal_rules.objectValues():\n
  if rule.getValidationState() != \'validated\':\n
    rule.validate()\n
\n
# Create resource\n
module = portal.getDefaultModule(resource_portal_type)\n
resource = module.newContent(\n
  portal_type=resource_portal_type,\n
  id=resource_id,\n
  title=resource_title\n
)\n
\n
# Create site categories\n
base_category = portal.restrictedTraverse(\'portal_categories/site\')\n
for site_id, site_title in ((source_site_id, source_site_title),\n
                (destination_site_id, destination_site_title)):\n
  site = base_category.newContent(\n
    portal_type=site_portal_type,\n
    id=site_id,\n
    title=site_title\n
  )\n
\n
# Create nodes\n
for node_id, node_title, site_url in ((source_node_id, source_node_title, source_site_id),\n
                          (destination_node_id, destination_node_title, destination_site_id)):\n
  module = portal.getDefaultModule(node_portal_type)\n
  node = module.newContent(\n
    portal_type=node_portal_type,\n
    id=node_id,\n
    title=node_title,\n
    site=site_url\n
  )\n
\n
# Reset selections\n
stool = context.getPortalObject().portal_selections\n
stool.setSelectionFor(\'resource_current_inventory\', None)\n
stool.setSelectionFor(\'movement_selection\', None)\n
\n
return "Reset Successfully."\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PdmZuite_reset</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
