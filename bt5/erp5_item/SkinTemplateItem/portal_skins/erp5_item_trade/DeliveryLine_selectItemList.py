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

from Products.ERP5Type.Message import translateString\n
item_list = []\n
portal = context.getPortalObject()\n
getObject = portal.portal_catalog.getObject\n
selection_tool = portal.portal_selections\n
\n
line_portal_type = context.getPortalType()\n
\n
if line_portal_type == \'Sale Packing List Line\':\n
  cell_portal_type = \'Sale Packing List Cell\'\n
elif line_portal_type == \'Sale Order Line\':\n
  cell_portal_type = \'Sale Order Cell\'\n
elif line_portal_type == \'Purchase Packing List Line\':\n
  cell_portal_type = \'Purchase Packing List Cell\'\n
elif line_portal_type == \'Inventory Line\':\n
  cell_portal_type = \'Inventory Cell\'\n
elif line_portal_type == \'Internal Packing List Line\':\n
  cell_portal_type = \'Internal Packing List Cell\'\n
else:\n
  raise NotImplementedError(\'Unknown line type %s\' % line_portal_type)\n
\n
\n
# update selected uids \n
selection_tool.updateSelectionCheckedUidList(\n
    list_selection_name, uids=uids, listbox_uid=listbox_uid, REQUEST=None)\n
uids = selection_tool.getSelectionCheckedUidsFor(list_selection_name)\n
\n
resource_uid_list = []\n
message = None\n
if not context.getResource():\n
  # Delivery line doesn\'t have resource defined yet.\n
  # Iterate over all selected items then check if they all\n
  # share the same resource. If not return to the dialog with warning message\n
  # otherwise edit the Delivery Line (context) with resource of all items.\n
  for item_uid in uids:\n
    item = getObject(item_uid)\n
    resource_item = item.Item_getResourceValue()\n
    if resource_item is None:\n
      message = portal.Base_translateString(\'Selected ${translated_portal_type} has no resource defined\',\n
                                            mapping={\'translated_portal_type\': item.getTranslatedPortalType().lower()})\n
      break\n
    if not resource_uid_list:\n
      # first item\n
      resource_uid_list.append(resource_item.getUid())\n
    elif resource_item.getUid() not in resource_uid_list:\n
      message = portal.Base_translateString(\'Selected ${translated_portal_type} does not share the same resource\',\n
                                            mapping={\'translated_portal_type\': item.getTranslatedPortalType().lower()})\n
      break\n
  if resource_uid_list and not message:\n
    # set resource on Delivery Line\n
    context.setResourceUid(resource_uid_list[0])\n
if message:\n
  # means that resource consistency fails.\n
  # One of Items does not have resource or Items does not share same resource\n
  # Script stop here\n
  context.Base_updateDialogForm(listbox=listbox,update=1, kw=kw)\n
  REQUEST = portal.REQUEST\n
  REQUEST.set(\'portal_status_message\', message)\n
  return getattr(context, REQUEST.form[\'dialog_id\'])(listbox=listbox, kw=kw)\n
\n
for item_uid in uids:\n
  item = getObject(item_uid)\n
  item_variation = \\\n
      item.Item_getVariationCategoryList(at_date=context.getStartDate())\n
  # if we have variation, find matching cell to add this item to the cell\n
  if item_variation:\n
    cell_found = None\n
    for cell in context.getCellValueList(base_id=\'movement\'):\n
      if cell.getVariationCategoryList() == item_variation:\n
        cell_found = cell\n
        break\n
    if cell_found is not None:\n
      movement_to_update = cell_found\n
    else:\n
      if not context.hasInRange(base_id=\'movement\', *item_variation):\n
        # update line variation category list, if not already containing this one\n
        variation_category_list = context.getVariationCategoryList()\n
        for variation in item_variation:\n
          if variation not in variation_category_list:\n
            variation_category_list.append(variation)\n
        context.setVariationCategoryList(variation_category_list)\n
\n
      movement_to_update = context.newCell(base_id=\'movement\',\n
                                           portal_type=cell_portal_type,\n
                                           *item_variation)\n
      movement_to_update.edit(mapped_value_property_list=(\'quantity\', \'price\'),\n
                              variation_category_list=item_variation,)\n
  else:\n
    # no variation, we\'ll update the line itself\n
    movement_to_update = context\n
\n
  movement_to_update.setAggregateValueSet(\n
      movement_to_update.getAggregateValueList() + [item])\n
\n
update_quantity = not context.Movement_isQuantityEditable()\n
if update_quantity:\n
  if context.isMovement():\n
    movement_list = context,\n
  else:\n
    movement_list = context.getCellValueList(base_id=\'movement\')\n
  for movement in movement_list:\n
    quantity = 0\n
    item_list = movement.getAggregateValueList()\n
    for item in item_list:\n
      if item.getQuantityUnit() != movement.getQuantityUnit():\n
        if len(item_list) > 1:\n
          raise NotImplementedError(\n
            \'Quantity unit from the movement differs from quantity\'\n
            \' unit on the item\')\n
        else:\n
          movement.setQuantityUnit(item.getQuantityUnit())\n
      quantity += item.getQuantity()\n
    movement.setQuantity(quantity)\n
  \n
return context.Base_redirect(form_id, keep_items=dict(\n
       portal_status_message=translateString(\'Items aggregated\')))\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id=\'view\', list_selection_name=\'\', uids=[], listbox=None, listbox_uid=[], *args, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>DeliveryLine_selectItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
