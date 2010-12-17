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

request = context.REQUEST\n
consumption_list = context.getSpecialiseValueList()\n
# convert string to float \n
reference_quantity = float( reference_quantity )\n
\n
cell_key_list = context.getCellKeyList( base_id = \'quantity\')\n
\n
for cell_key in cell_key_list:\n
\n
  # If cell exists, do not modify it\n
  if not context.hasCell(base_id=\'quantity\', *cell_key ):\n
    ratio = 1\n
    consumption_applied = 0\n
\n
    # XXX This part can be really improve, but it works\n
    for reference_variation_category in reference_variation_category_list:\n
      for consumption in consumption_list:\n
        for key in cell_key:\n
          consumption_ratio = consumption.getQuantityRatio(reference_variation_category, key )\n
          if consumption_ratio is not None:\n
            ratio = ratio * consumption_ratio\n
            consumption_applied = 1\n
          \n
    # If no consumption applied, do not do anything\n
    if consumption_applied:\n
      cell = context.newCell(base_id=\'quantity\', *cell_key)\n
      cell.edit(mapped_value_property_list = [\'quantity\'],\n
                quantity = ratio * reference_quantity \n
      )\n
      cell.setMembershipCriterionCategoryList( cell_key )\n
      cell.setMembershipCriterionBaseCategoryList( context.getQVariationBaseCategoryList() )\n
\n
redirect_url = \'%s/%s?%s&%s&%s\' % ( context.absolute_url()\n
                              , form_id\n
                              , \'selection_index=%s\' % selection_index\n
                              , \'selection_name=%s\' % selection_name\n
                              , \'portal_status_message=Consumption+applied.\'\n
                              )\n
return request[ \'RESPONSE\' ].redirect( redirect_url )\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>reference_variation_category_list, reference_quantity, form_id, selection_index=0, selection_name=\'\'</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TransformedResource_completeQuantityMatrix</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
