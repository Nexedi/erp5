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

rate_list = context.CurrencyExchange_getExchangeRateList()\n
rate = None\n
if len(rate_list) > 0:\n
 rate = rate_list[1]\n
if rate is None:\n
  return None\n
\n
base_price = context.getSourceTotalAssetPrice()\n
if base_price is None:\n
  return None\n
\n
price = rate * base_price\n
\n
commission_ratio = context.getDiscountRatio()\n
commission_price = context.getDiscount()\n
if commission_ratio is not None and commission_ratio !=0 and commission_price is not None and commission_price !=0:\n
  return None\n
if (commission_ratio is None or commission_ratio == 0) and (commission_price is None or commission_price == 0):\n
  return None\n
\n
if commission_ratio is not None:\n
  commission_value = commission_ratio * price\n
\n
if commission_price is not None:\n
  commission_value = commission_price\n
\n
\n
quantity = price + commission_value\n
context.setQuantity(quantity)\n
return quantity\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CashToCurrencySale_getQuantity</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
