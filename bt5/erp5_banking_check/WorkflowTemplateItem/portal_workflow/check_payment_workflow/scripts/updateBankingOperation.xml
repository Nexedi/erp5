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
            <value> <string># Note: this script is executed with the proxy role Manager, because this script needs\n
#       to use checkbook_module.\n
from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
from Products.ERP5Type.Message import Message\n
\n
transaction = state_change[\'object\']\n
bank_account = transaction.getDestinationPaymentValue()\n
check_number = transaction.getAggregateFreeText()\n
\n
# Already done before in validateConsistency\n
#check = transaction.Base_checkOrCreateCheck(reference=check_number)\n
#if not check.Check_isValid():\n
#  raise ValidationFailed, Message(domain=\'ui\', message=\'Check is in an invalid state\')\n
\n
line = transaction.get(\'movement\')\n
if line is not None and line.getPortalType() == \'Banking Operation Line\':\n
  # This is a single currency operation, so it is not necessary to convert the price.\n
  line.setSourceDebit(transaction.getSourceTotalAssetPrice())\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
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
            <value> <string>updateBankingOperation</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
