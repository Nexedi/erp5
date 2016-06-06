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
            <value> <string># check if the user is Anonymous, if yes it must be redirected to Registration Dialog\n
# otherwise it will redirect to the appropriated payment form based on Payment Mode selected\n
request = context.REQUEST\n
isAnon = context.portal_membership.isAnonymousUser()\n
translateString = context.Base_translateString\n
\n
if field_my_comment is not None:\n
  shopping_cart = context.SaleOrder_getShoppingCart()\n
  shopping_cart.setComment(field_my_comment)\n
\n
if isAnon:\n
  # create first an account for user\n
  web_site = context.getWebSiteValue()\n
  msg = translateString("You need to create an account to continue. If you already have please login.")\n
  web_site.Base_redirect(\'register\', \\\n
                      keep_items={\'portal_status_message\': msg})\n
  return\n
\n
if field_my_payment_mode is None:\n
  msg = translateString("You must select a payment mode.")\n
else:\n
  if field_my_payment_mode.lower() == \'credit card\':\n
    return context.getWebSectionValue().SaleOrder_viewAsWebConfirmCreditCardPayment()\n
  elif field_my_payment_mode.lower() == \'paypal\':\n
    return context.getWebSectionValue().SaleOrder_viewAsWebConfirmPayPalPayment()\n
  else:\n
    msg = translateString("This payment mode is actually not activated, sorry: ${payment_mode}", \n
                          mapping=dict(payment_mode=field_my_payment_mode))\n
\n
context.Base_redirect(\'SaleOrder_viewAsWeb\', \\\n
                        keep_items={\'portal_status_message\': msg})\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>field_my_comment=None, field_my_payment_mode=None, **kw</string> </value>
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
            <value> <string>SaleOrder_paymentRedirect</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
