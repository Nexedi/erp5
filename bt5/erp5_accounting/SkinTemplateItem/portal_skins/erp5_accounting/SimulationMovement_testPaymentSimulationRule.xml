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
            <value> <string>movement = context\n
\n
parent = movement.getParentValue()\n
if parent.getPortalType() != \'Applied Rule\':\n
  return False\n
\n
if parent.getSpecialiseReference() != \'default_invoice_transaction_rule\':\n
  return False\n
\n
# XXX hardcoded\n
receivable_account_type_list = (\'asset/receivable\',)\n
payable_account_type_list = (\'liability/payable\',)\n
\n
for account in (movement.getSourceValue(portal_type=\'Account\'),\n
                movement.getDestinationValue(portal_type=\'Account\')):\n
  if account is not None:\n
    account_type = account.getAccountType()\n
    if account_type in receivable_account_type_list or \\\n
        account_type in payable_account_type_list:\n
      return True\n
\n
return False\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>rule</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SimulationMovement_testPaymentSimulationRule</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
