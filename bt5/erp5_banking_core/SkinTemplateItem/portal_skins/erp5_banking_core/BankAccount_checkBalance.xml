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

# check that the amount of `resource` in account `payment` is greater than or equal to `quantity`\n
# returns a dictionnary like : {\'error_code\', \'balance\'}\n
\n
# First check that the payment account is in an acceptable state\n
payment_value = context.restrictedTraverse(payment)\n
\n
if not payment_value.BankAccount_isOpened():\n
  return {\'error_code\': 2} # closed account\n
\n
account_balance = payment_value.BankAccount_getAvailablePosition(src__=src__)\n
if src__:\n
  return account_balance\n
# XXX: BankAccount_getAvailablePosition returns position as a string for some reason...\n
raw_account_balance = account_balance = float(account_balance)\n
if round_balance:\n
  account_balance = round(account_balance, payment_value.getPriceCurrencyValue().getQuantityPrecision())\n
\n
if account_balance - quantity < 0:\n
  # insufficient balance\n
  return {\n
    \'error_code\': 1,\n
    \'balance\': account_balance,\n
    \'raw_balance\': raw_account_balance,\n
  }\n
\n
payment_value.serialize()\n
return {\n
  \'error_code\': 0,\n
  \'balance\': account_balance,\n
  \'raw_balance\': raw_account_balance,\n
}\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>payment, quantity, round_balance=True, src__=0</string> </value>
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
            <value> <string>BankAccount_checkBalance</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
