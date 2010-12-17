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
            <value> <string>from Products.ERP5Type.Utils import cartesianProduct\n
from Products.ERP5Type.Message import translateString\n
\n
updated_cell_count = 0\n
\n
dependant_dimensions_dict = context.BudgetLine_getSummaryDimensionKeyDict()\n
cell_key_list = context.getCellKeyList()\n
\n
def reversed(seq):\n
  seq = seq[::]\n
  seq.sort(reverse=True)\n
  return seq\n
\n
# we iterate in reversed order to update the deepest cells first\n
for cell_key in reversed(cartesianProduct(context.getCellRange())):\n
  for idx, dimension in enumerate(cell_key):\n
    if dimension in dependant_dimensions_dict:\n
      dependant_cell_list = []\n
      matching_cell_key = list(cell_key)\n
      for key in dependant_dimensions_dict[dimension]:\n
        matching_cell_key[idx] = key\n
        for other_cell_key in cell_key_list:\n
          if matching_cell_key == other_cell_key:\n
            cell = context.getCell(*other_cell_key)\n
            if cell is not None:\n
              dependant_cell_list.append(cell)\n
\n
      if dependant_cell_list:\n
        cell = context.getCell(*cell_key)\n
        if cell is None:\n
          # if summary cell does not exist, we create it.\n
          cell = context.newCell(*cell_key)\n
          cell.edit(\n
            membership_criterion_base_category_list\n
              =[bc for bc in context.getVariationBaseCategoryList() if bc not\n
                in context.getMembershipCriterionBaseCategoryList()],\n
            membership_criterion_category_list=cell_key,\n
            mapped_value_property_list=(\'quantity\', ))\n
        cell.setQuantity(sum([dependant_cell.getQuantity() for dependant_cell\n
                                in dependant_cell_list]))\n
        updated_cell_count += 1\n
      break\n
\n
return context.Base_redirect(form_id,\n
     keep_items=dict(portal_status_message=translateString(\n
      "${updated_cell_count} budget cells updated.",\n
      mapping=dict(updated_cell_count=updated_cell_count))))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id=\'view\'</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BudgetLine_setQuantityOnSummaryCellList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
