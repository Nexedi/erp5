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

rate = None\n
method = getattr(context, \'getCurrencyExchangeRate\', None)\n
if method is not None:\n
  rate = method()\n
if rate is None:\n
  rate_list = context.CurrencyExchange_getExchangeRateList(from_currency=from_currency,\n
                 to_currency=to_currency, \n
                 currency_exchange_type=currency_exchange_type,\n
                 start_date=start_date)\n
  if len(rate_list) > 0:\n
    rate = rate_list[0]\n
\n
price = context.getSourceTotalAssetPrice()\n
\n
if None in (rate, price):\n
  return None\n
\n
price = float(price)\n
\n
return round(rate * price)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>from_currency=None,to_currency=None, currency_exchange_type=None, start_date=None</string> </value>
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
            <value> <string>ERP5Banking_getExchangeValue</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
