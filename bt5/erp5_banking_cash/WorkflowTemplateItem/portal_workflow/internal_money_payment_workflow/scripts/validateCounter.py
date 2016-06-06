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
\n
\n
# check we are in an opened accounting day\n
transaction.Baobab_checkCounterDateOpen(site=source, date=transaction.getStartDate())\n
\n
\n
# check again that the counter is open\n
\n
context.Baobab_checkCounterOpened(source)\n
\n
if transaction.getPaymentType() in (None, ""):\n
  msg = Message(domain="ui", message="No payment type defined.")\n
  raise ValidationFailed, (msg,)\n
\n
\n
#test if the source or the destination is correct\n
transaction.Base_checkBaobabSourceAndDestination()\n
\n
# Get price and total_price.\n
amount = transaction.getSourceTotalAssetPrice()\n
total_price = transaction.getTotalPrice(portal_type=(\'Cash Delivery Line\',\'Cash Delivery Cell\'), fast=0)\n
\n
if amount != total_price:\n
  msg = Message(domain="ui", message="Amount differ from total price.")\n
  raise ValidationFailed, (msg,)\n
\n
if source is None:\n
  msg = Message(domain=\'ui\', message=\'No counter defined.\')\n
  raise ValidationFailed, (msg,)\n
\n
\n
\n
site = transaction.getSourceValue()\n
\n
\n
\n
vault = transaction.getBaobabSource()\n
resource = transaction.CashDelivery_checkCounterInventory(source=vault, portal_type=\'Cash Delivery Line\',same_source=1)\n
\n
#context.log(\'resource\',resource)\n
\n
if resource == 2:\n
  msg = Message(domain="ui", message="No Resource.")\n
  raise ValidationFailed, (msg,)\n
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
            <value> <string>validateCounter</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
