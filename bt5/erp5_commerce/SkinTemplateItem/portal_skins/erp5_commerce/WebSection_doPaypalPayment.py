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
            <value> <string>request = context.REQUEST\n
isAnon = context.portal_membership.isAnonymousUser()\n
translateString = context.Base_translateString\n
\n
## check if user is authenticated\n
if isAnon:\n
  msg = translateString("You need to create an account to continue. If you already have one, please login.")\n
  context.Base_redirect(\'WebSite_viewRegistrationDialog\', \\\n
                        keep_items={\'portal_status_message\': msg,\n
                                    \'editable_mode\': 1})\n
  return\n
\n
## check if the id of the token correspond to the good products\n
parameter_dict = context.WebSection_getExpressCheckoutDetails(token)\n
if parameter_dict[\'ACK\'] != \'Success\':\n
  msg = translateString("This paypal session is not initialised with the actual card.")\n
  context.Base_redirect(\'\', \\\n
                        keep_items={\'portal_status_message\': msg,})\n
\n
payer_id = parameter_dict[\'PAYERID\']\n
response_dict = context.WebSection_doExpressCheckoutPayment(token, payer_id)\n
\n
if response_dict[\'ACK\'] != \'Success\':\n
  msg = translateString("Your payment failed because of ")\n
  context.Base_redirect(\'WebSite_viewRegistrationDialog\', \\\n
                        keep_items={\'portal_status_message\': \'%s : %s\' % (msg, str(response_dict)),\n
                                    \'editable_mode\': 1})\n
  return\n
\n
#Payment is ok. Set shopping cart is payed\n
context.SaleOrder_setShoppingCartBuyer()\n
  \n
return context.SaleOrder_finalizeShopping()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>token</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSection_doPaypalPayment</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
