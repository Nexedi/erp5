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

# first we build a dict of desired container lines\n
# key of dict : id of resource\n
# item of dict : tuples (resource_value, variation_category_list, quantity)\n
from ZTUtils import make_query\n
\n
delivery = context\n
next_container_number = next_container_int_index\n
\n
desired_lines = {}\n
quantity_unit_dict = {}\n
\n
for listitem in listbox :\n
  movement_relative_url = listitem[\'listbox_key\']\n
  container_quantity = listitem[\'container_quantity\']\n
  if container_quantity :\n
    movement = context.restrictedTraverse(movement_relative_url)\n
    if movement is not None:\n
      resource = movement.getResourceValue()\n
      if resource is not None:\n
        quantity_unit_dict[resource.getRelativeUrl()] =\\\n
                                                movement.getQuantityUnit()\n
        if resource.getRelativeUrl() in desired_lines.keys():\n
          desired_lines[resource.getRelativeUrl()].append(\n
                                  (movement.getVariationCategoryList(),\n
                                  container_quantity))\n
        else :\n
          desired_lines[resource.getRelativeUrl()] = [\n
                                  (movement.getVariationCategoryList(),\n
                                  container_quantity)]\n
\n
# we build \'container_count\' containers \n
for container_number in range(container_count) :\n
\n
  new_container_id = \'c\'+str(next_container_number)\n
  # we use container_type to know which are the resource (and variation) \n
  # of the container\n
  container = delivery.newContent(\n
                          portal_type="Container",\n
                          title=new_container_id,\n
                          int_index=next_container_number,\n
                          serial_number="%06d%04d" % (int(delivery.getId()),\n
                                                      next_container_number),\n
                          resource = container_type,\n
                          gross_weight = gross_weight,\n
  )\n
\n
  next_container_number += 1\n
\n
  # now build container_lines\n
  for resource_url in desired_lines.keys():\n
\n
    # compute variation_base_category_list and variation_category_list for this line\n
    line_variation_base_category_dict = {}\n
    line_variation_category_list = []\n
\n
    for variation_category_list, quantity in desired_lines[resource_url]:\n
\n
      for variation_item in variation_category_list:\n
        if not variation_item in line_variation_category_list :\n
          line_variation_category_list.append(variation_item)\n
          variation_base_category_items = variation_item.split(\'/\')\n
          if len(variation_base_category_items) > 0 :\n
            line_variation_base_category_dict[variation_base_category_items[0]] = 1\n
\n
      line_variation_base_category_list = line_variation_base_category_dict.keys()\n
\n
    # construct new content (container_line)\n
    resource_url = resource_url\n
    new_container_line_id = str(container.generateNewId())\n
    container_line = container.newContent(\n
                portal_type="Container Line",\n
                title=new_container_line_id,\n
                resource=resource_url,\n
                quantity_unit=quantity_unit_dict[resource_url],\n
                variation_category_list=line_variation_category_list\n
    )\n
\n
    for cell_key, quantity in desired_lines[resource_url]:\n
      if variation_category_list == []:\n
        container_line.edit(quantity=quantity)\n
      else:\n
        # create a new cell\n
        base_id = \'movement\'\n
        if not container_line.hasCell(base_id=base_id, *cell_key):\n
          cell = container_line.newCell(\n
                     base_id=base_id,\n
                     portal_type="Container Cell",\n
                     *cell_key\n
          )\n
          cell.setCategoryList(cell_key)\n
          cell.setMappedValuePropertyList([\'quantity\'])\n
          cell.setMembershipCriterionCategoryList(cell_key)\n
          cell.setMembershipCriterionBaseCategoryList(\n
                                          line_variation_base_category_list)\n
          cell.edit(quantity=quantity)\n
\n
# Container must be immediately reindexed, \n
# in order to see good packed quantity in fast input form\n
container.recursiveImmediateReindexObject()\n
\n
url_params = make_query(selection_name=selection_name, \n
                        dialog_category=dialog_category, \n
                        form_id=form_id, \n
                        cancel_url=cancel_url,\n
                        portal_status_message=\'%s container(s) created.\' %\\\n
                                                                container_count)\n
\n
redirect_url = \'%s/SalePackingList_fastInputForm?%s\' %\\\n
                            (context.absolute_url(), url_params)\n
\n
context.REQUEST[ \'RESPONSE\' ].redirect(redirect_url)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id=\'\',selection_index=None,selection_name=\'\',dialog_category=\'object_exchange\',container_count=0,container_type=\'\',gross_weight=0,listbox=[],cancel_url=\'\',next_container_int_index=1,**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SalePackingList_fastInput</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
