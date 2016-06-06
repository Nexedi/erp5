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
            <value> <string>from Products.ERP5Type.Message import translateString\n
\n
source = context.Item_getCurrentSiteValue()\n
source_section = context.Item_getCurrentOwnerValue()\n
\n
module = context.getDefaultModule(portal_type=portal_type)\n
line_portal_type = \'%s Line\' % portal_type\n
cell_portal_type = \'%s Cell\' % portal_type\n
\n
delivery = module.newContent(title=title,\n
                             source_value=source,\n
                             source_section_value=source_section,\n
                             portal_type=portal_type)\n
                          \n
delivery_line = delivery.newContent(\n
                    portal_type=line_portal_type,\n
                    title=context.getReference(),\n
                    quantity_unit=context.getQuantityUnit(),\n
                    resource_value=context.Item_getResourceValue())\n
\n
variation_category_list = context.Item_getVariationCategoryList()\n
\n
if not variation_category_list:\n
  delivery_line.edit(\n
              price=context.getPrice(),\n
              quantity=context.getQuantity(),\n
              aggregate_value=context)\n
else:\n
  delivery_line.setVariationCategoryList(variation_category_list)\n
  base_id = \'movement\'\n
  cell_key_list = list(delivery_line.getCellKeyList(base_id=base_id))\n
  cell_key_list.sort()\n
  for cell_key in cell_key_list:\n
    cell = delivery_line.newCell(base_id=base_id,\n
                                 portal_type=cell_portal_type,\n
                                 *cell_key)\n
    cell.edit(mapped_value_property_list=[\'price\',\'quantity\'],\n
              price=context.getPrice(),\n
              quantity=context.getQuantity(),\n
              predicate_category_list=cell_key,\n
              variation_category_list=cell_key,\n
              aggregate_value=context)\n
\n
return delivery.Base_redirect(\'view\', keep_items=dict(\n
                                 portal_status_message=translateString(\'Item affected\')))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id=\'view\', title=\'\', portal_type=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Item_createDeliveryLine</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
