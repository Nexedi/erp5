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
            <value> <string>translateString = context.Base_translateString\n
\n
token = context.REQUEST.get(\'token\')\n
payer_id = context.REQUEST.get(\'PayerID\')\n
\n
parameter_dict = context.WebSection_getExpressCheckoutDetails(token)\n
\n
if parameter_dict[\'ACK\'] != \'Success\':\n
  return "Identification failed.1 : %s" % parameter_dict[\'ACK\']\n
\n
if parameter_dict[\'PAYERID\'] != payer_id:\n
  return "Identification failed.2 : %s" % parameter_dict[\'PAYERID\']\n
\n
#redirect user to the checkout section\n
website = context.getWebSiteValue() \n
section_url = website.getLayoutProperty(\'ecommerce_checkout_section_id\',"checkout")\n
website.Base_redirect(section_url, \\\n
                       keep_items={\'portal_status_message\':translateString("The payment procedure went well on Paypal."),\n
                                      \'token\':token})\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSection_checkPaypalIdentification</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
