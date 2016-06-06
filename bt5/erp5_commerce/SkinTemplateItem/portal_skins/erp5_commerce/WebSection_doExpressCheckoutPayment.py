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
            <value> <string>order_parameter_dict = context.WebSite_getPaypalOrderParameterDict()\n
if order_parameter_dict is None:\n
  return None\n
order_parameter_dict[\'TOKEN\'] = token\n
order_parameter_dict[\'PAYERID\'] = payer_id\n
order_parameter_dict[\'METHOD\'] = \'DoExpressCheckoutPayment\'\n
\n
response_parameter_dict = context.WebSection_submitPaypalNVPRequest(parameter_dict=order_parameter_dict,\n
                                                                  nvp_url=context.WebSite_getPaypalUrl(api=\'nvp\'))\n
return response_parameter_dict\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>token, payer_id</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSection_doExpressCheckoutPayment</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
