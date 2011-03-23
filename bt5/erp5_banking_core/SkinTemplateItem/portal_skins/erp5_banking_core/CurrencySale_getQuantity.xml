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
            <value> <string>price = context.ERP5Banking_getExchangeValue()\n
if price is None:\n
  return price\n
\n
commission_ratio = context.getDiscountRatio()\n
commission_price = context.getDiscount()\n
if commission_ratio is not None and commission_ratio !=0 and commission_price is not None and commission_price !=0:\n
  price = None\n
elif commission_ratio == 0 or commission_price == 0:\n
  price = round(price,0)\n
elif commission_ratio is None and commission_price is None:\n
  price = round(price,0)\n
\n
commission_value = 0\n
if commission_ratio is not None:\n
  commission_value = commission_ratio * price\n
\n
if commission_price is not None:\n
  commission_value = commission_price\n
\n
if price is None:\n
  return price\n
\n
quantity = price + commission_value\n
quantity = round(quantity,0)\n
if quantity!=context.getQuantity():\n
  context.setQuantity(quantity)\n
return quantity\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CurrencySale_getQuantity</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
