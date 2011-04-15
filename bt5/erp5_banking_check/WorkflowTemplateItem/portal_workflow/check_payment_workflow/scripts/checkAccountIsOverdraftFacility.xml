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
            <value> <string>from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
from Products.ERP5Type.Message import Message\n
\n
transaction = state_change[\'object\']\n
date = transaction.getStartDate()\n
source = transaction.getSource(None)\n
if source is None:\n
  msg = Message(domain=\'ui\', message=\'No counter defined.\')\n
  raise ValidationFailed, (msg,)\n
\n
# check we are in an opened accounting day\n
transaction.Baobab_checkCounterDateOpen(site=source, date=date)\n
\n
site = transaction.getSourceValue()\n
\n
# For safety, check the consistency again.\n
context.validateConsistency(state_change, no_balance_check=1)\n
\n
line = transaction.movement\n
bank_account = transaction.getDestinationPaymentValue()\n
\n
if not bank_account.isOverdraftFacility():\n
  msg = Message(domain=\'ui\', message="Can\'t sent to manual validation because of not overdraft facility for this bank account")\n
  raise ValidationFailed, (msg,)\n
\n
price = transaction.getSourceTotalAssetPrice()\n
\n
# this prevents multiple transactions from being committed at the same time for this bank account.\n
bank_account.serialize()\n
\n
# Make sure there are no other operations pending for this account\n
if transaction.BankAccount_isMessagePending(bank_account):\n
  msg = Message(domain=\'ui\', message="There are operations pending for this account that prevent form calculating its position. Please try again later.")\n
  raise ValidationFailed, (msg,)\n
\n
# Index the banking operation line so it impacts account position\n
transaction.BankingOperationLine_index(line)\n
\n
# Check if the banking operation is correct. Do not depend on catalog because line might not be indexed immediatelly.\n
if - price != (line.getPrice() * line.getQuantity()):\n
  msg = Message(domain=\'ui\', message=\'Banking operation and check payment price do not match.\')\n
  raise ValidationFailed, (msg,)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>checkAccountIsOverdraftFacility</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
