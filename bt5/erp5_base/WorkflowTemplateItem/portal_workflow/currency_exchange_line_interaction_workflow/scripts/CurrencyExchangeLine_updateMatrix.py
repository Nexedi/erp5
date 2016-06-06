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
            <value> <string>context = state_change[\'object\']\n
\n
base_id = \'path\'\n
kwd = {\'base_id\': base_id}\n
\n
\n
context.updateCellRange(script_id=\'CurrencyExchangeLine_asCellRange\', base_id=base_id)\n
cell_range_key_list = context.getCellRangeKeyList(base_id = base_id)\n
resource_list = [\'resource/%s\' % context.getParentValue().getRelativeUrl()]\n
price_currency_list = [context.getPriceCurrency(base=True)]\n
membership_list = resource_list + price_currency_list\n
context.setMembershipCriterionBaseCategoryList([x.split(\'/\')[0] for x in membership_list])\n
context.setMembershipCriterionCategoryList(membership_list)\n
context.setResourceValue(context.getParentValue())\n
context.setMappedValuePropertyList((\'base_price\',\'discount\'))\n
if cell_range_key_list != [[None, None]] :\n
  i = 0\n
  for k in cell_range_key_list:\n
    category_list = filter(lambda k_item: k_item is not None, k)\n
    c = context.newCell(*k, **kwd)\n
    c.edit(mapped_value_property_list = (\'base_price\',\'discount\'),\n
           force_update = 1,\n
           membership_criterion_base_category_list = [x.split(\'/\')[0] for x in category_list],\n
           membership_criterion_category_list = category_list,\n
           category_list = category_list,\n
    )\n
    c.setCriterion(\'stop_date\', min=context.getStartDate(), max=context.getStopDate())\n
    if c.getBasePrice() is None and context.getBasePrice() is not None:\n
      c.setBasePrice(context.getBasePrice())\n
    # set an int index for display\n
    currency_exchange_type_value_list = c.getValueList(\'currency_exchange_type\')\n
    if currency_exchange_type_value_list:\n
      c.setIntIndex(currency_exchange_type_value_list[0].getIntIndex())\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CurrencyExchangeLine_updateMatrix</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
