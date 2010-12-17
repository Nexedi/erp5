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
            <value> <string>if related_simulation_movement_path_list is None:\n
  raise RuntimeError, \'related_simulation_movement_path_list is missing. Update ERP5 Product.\'\n
\n
open_sale_order = context.getCausalityValue()\n
\n
open_sale_order_trade_condition = open_sale_order.getSpecialiseValue()\n
if open_sale_order_trade_condition is not None:\n
  context.setSpecialise(open_sale_order_trade_condition.getRelativeUrl())\n
  context.Order_applyTradeCondition(open_sale_order_trade_condition)\n
context.order(comment=\'Ordered by Open Sale Order\')\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>related_simulation_movement_path_list=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SaleOrder_copyOpenSaleOrderProperties</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
