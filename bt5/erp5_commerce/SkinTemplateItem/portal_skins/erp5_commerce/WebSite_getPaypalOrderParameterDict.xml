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
            <value> <string>order_parameter_dict = context.WebSite_getPaypalSecurityParameterDict()\n
if order_parameter_dict is None:\n
  return None\n
\n
web_site = context.getWebSiteValue()\n
shopping_cart = context.SaleOrder_getShoppingCart()\n
shopping_cart_product_list = shopping_cart.SaleOrder_getShoppingCartItemList()\n
shopping_cart_price = float(web_site.SaleOrder_getShoppingCartTotalPrice())\n
taxes_amount = float(shopping_cart.SaleOrder_getShoppingCartTotalPrice(include_taxes=True, include_shipping=True)) - \\\n
               float(shopping_cart.SaleOrder_getShoppingCartTotalPrice(include_shipping=True));\n
if shopping_cart.SaleOrder_isShippingRequired():\n
  shipping = shopping_cart.SaleOrder_getSelectedShippingResource()\n
  shipping_price = shipping.getPrice()\n
else:\n
  shipping_price = 0\n
\n
customer = context.SaleOrder_getShoppingCartCustomer()\n
site_url = web_site.absolute_url()\n
\n
order_parameter_dict[\'METHOD\'] = \'SetExpressCheckout\'\n
order_parameter_dict[\'RETURNURL\'] = \'%s/WebSection_checkPaypalIdentification\' % site_url\n
order_parameter_dict[\'CANCELURL\'] = site_url\n
order_parameter_dict[\'PAYMENTACTION\'] = \'Sale\'\n
\n
actual_product_index = 0\n
for product in shopping_cart_product_list:\n
  resource = context.restrictedTraverse(product.getResource())\n
  quantity = int(product.getQuantity())\n
  price = resource.getPrice()\n
  order_parameter_dict[\'L_NAME%s\' % actual_product_index] = resource.getTitle()\n
  order_parameter_dict[\'L_NUMBER%s\' % actual_product_index] = resource.getId()\n
  order_parameter_dict[\'L_AMT%s\' % actual_product_index] = price\n
  order_parameter_dict[\'L_QTY0%s\' % actual_product_index] = quantity\n
  actual_product_index += 1\n
\n
order_parameter_dict[\'ITEMAMT\'] = shopping_cart_price\n
order_parameter_dict[\'TAXAMT\'] = taxes_amount\n
order_parameter_dict[\'SHIPPINGAMT\'] = shipping_price\n
order_parameter_dict[\'AMT\'] = shopping_cart_price + taxes_amount + shipping_price\n
order_parameter_dict[\'CURRENCYCODE\'] = context.WebSite_getShoppingCartDefaultCurrencyCode()\n
order_parameter_dict[\'NOSHIPPING\'] = str(not shopping_cart.SaleOrder_isShippingRequired())\n
order_parameter_dict[\'ALLOWNOTE\'] = \'0\'\n
\n
return order_parameter_dict\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSite_getPaypalOrderParameterDict</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
