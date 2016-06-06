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
            <value> <string>""" \n
  Calculate total price of temporary RAM based Sale Order.\n
\n
  Price is based on three main components:\n
    - shopping cart items\n
    - applicable taxes (based on Person\'s location and shop\'s location)\n
    - shipping costs (same as applicable taxes including type of shopping cart item\n
      for example online materials doesn\'t require shipping)\n
  \n
  Script can optionally include currency.\n
"""\n
\n
web_site = context.getWebSiteValue()\n
total = 0.0\n
shopping_cart_item_list = context.SaleOrder_getShoppingCartItemList(include_shipping)\n
for order_line in shopping_cart_item_list:\n
  resource = context.restrictedTraverse(order_line.getResource())\n
  if order_line.getPrice() is not None:\n
    total += order_line.getPrice() * order_line.getQuantity()\n
\n
# XXX: CHECK if we have to include taxes on shipping service\n
if include_taxes:\n
  tax_info = context.Person_getApplicableTaxList()\n
  if tax_info is not None:\n
    for tax in tax_info.values():\n
      total += total*(tax[\'percent\']/100)\n
    \n
if include_currency:\n
  currency = web_site.WebSite_getShoppingCartDefaultCurrency()\n
  return \'%s %s\' %(total, currency.getReference())\n
else:\n
  return str(total)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>include_shipping=False, include_taxes=False, include_currency = False</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SaleOrder_getShoppingCartTotalPrice</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Calculate total price for items in shopping cart</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
