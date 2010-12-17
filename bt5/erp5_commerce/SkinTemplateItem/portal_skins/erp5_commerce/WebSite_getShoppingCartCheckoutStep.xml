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
  Return the current step for checkout procedure that will be displayed on Shopping Cart page.\n
"""\n
web_site = context.getWebSiteValue()\n
shopping_cart = web_site.SaleOrder_getShoppingCart()\n
empty_cart = shopping_cart.SaleOrder_isShoppingCartEmpty()\n
is_consistent = shopping_cart.SaleOrder_isConsistent()\n
is_anonymous = context.portal_membership.isAnonymousUser()\n
\n
if empty_cart:\n
  return context.Base_translateString(\'Add a product to your Shopping Cart.\')\n
\n
if not is_consistent:\n
  return context.Base_translateString(\'Select a Shipping Service.\')\n
\n
if is_consistent and is_anonymous:\n
  return context.Base_translateString(\'Please, you must login to proceed.\')\n
\n
if is_consistent and not is_anonymous:\n
  return context.Base_translateString(\'Select your billing address.\')\n
\n
return\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSite_getShoppingCartCheckoutStep</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Get current Shopping Cart step for checkout procedure.</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
