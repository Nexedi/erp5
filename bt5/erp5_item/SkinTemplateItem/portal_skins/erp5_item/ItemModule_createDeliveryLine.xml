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
            <value> <string># Creates one Order/Packing list per Different Source sections\n
# Creates one Line per Resource\n
from Products.ERP5Type.Message import translateString\n
selection_name = "item_module_selection"\n
cell_portal_type = \'%s Cell\' % portal_type\n
portal = context.getPortalObject()\n
stool = portal.portal_selections\n
getObject = portal.portal_catalog.getObject\n
\n
\n
selection_uid_list = stool.getSelectionCheckedUidsFor(selection_name)\n
\n
if selection_uid_list:\n
  object_list = [getObject(uid) for uid in selection_uid_list]\n
else:\n
  object_list = stool.callSelectionFor(selection_name)\n
\n
source_section_list = [  item.Item_getCurrentOwnerValue() for item in object_list ]\n
\n
property_dict = {\'title\':title,\n
                 \'portal_type\' : portal_type, }\n
\n
module = context.getDefaultModule(portal_type=portal_type)\n
line_portal_type = \'%s Line\' % portal_type\n
\n
pl_property_dict = {}\n
for k,v in property_dict.items():\n
  pl_property_dict[k]=v\n
\n
pl_dict = {}\n
\n
for ss in source_section_list:\n
  if ss is not None:\n
    uid = str(ss.getUid())\n
  else:\n
    uid = \'UID\' \n
\n
  if not pl_dict.has_key(uid):\n
    pl_dict[uid] = module.newContent(**pl_property_dict)\n
    pl_dict[uid].setSourceSectionValue(ss)\n
\n
delivery_count = len(source_section_list)\n
\n
for item in object_list:\n
  source_section = item.Item_getCurrentOwnerValue()\n
  if source_section is not None:\n
    if source_section.getUid() is not None:\n
      pl_value =  pl_dict[str(source_section.getUid())]\n
  else:\n
    pl_value =  pl_dict[\'UID\']\n
\n
  source = item.Item_getCurrentSiteValue() \n
  resource = item.Item_getResourceValue()\n
\n
  pl_line_dict = {}\n
  pl_line_dict[\'portal_type\'] = line_portal_type\n
  \n
  pl_line_dict[\'title\']= item.getReference()\n
  pl_line_dict[\'quantity\'] = item.getQuantity()\n
  pl_line_dict[\'quantity_unit\'] = item.getQuantityUnit()\n
  pl_line_dict[\'resource_value\'] = resource\n
  pl_line_dict[\'source_value\'] = source\n
  pl_line_value = pl_value.newContent(**pl_line_dict)\n
  variation_category_list = item.Item_getVariationCategoryList()\n
  if not variation_category_list:\n
    pl_line_value.setAggregateValue(item)\n
  else:\n
    pl_line_value.setVariationCategoryList(variation_category_list)\n
    base_id = \'movement\'\n
    cell_key_list = list(pl_line_value.getCellKeyList(base_id=base_id))\n
    cell_key_list.sort()\n
    for cell_key in cell_key_list:\n
      cell = pl_line_value.newCell(base_id=base_id, \\\n
                                portal_type=cell_portal_type,*cell_key)\n
      cell.edit(mapped_value_property_list=[\'price\',\'quantity\'],\n
                price=item.getPrice(), quantity=item.getQuantity(),\n
                predicate_category_list=cell_key,\n
                variation_category_list=cell_key)\n
      cell.setAggregateValue(item)\n
\n
if delivery_count == 1:\n
  return pl_value.Base_redirect(\'view\', keep_items=dict(\n
       portal_status_message=translateString(\n
         \'Items affected\')))\n
\n
return context.Base_redirect(form_id, keep_items=dict(\n
       portal_status_message=translateString(\n
         \'Items affected in ${delivery_count} deliveries.\',\n
         mapping=dict(delivery_count=delivery_count))))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id=\'view\', title=\'\', portal_type=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ItemModule_createDeliveryLine</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
