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
\n
date = transaction.getStartDate()\n
destination= transaction.getDestination()\n
# check we are in an opened accounting day\n
transaction.Baobab_checkCounterDateOpen(site=destination, date=transaction.getStartDate())\n
\n
site = transaction.getDestinationValue()\n
\n
# check again that the counter is open\n
\n
context.Baobab_checkCounterOpened(destination)\n
\n
if transaction.getResource() is None:\n
  msg = Message(domain="ui", message="No resource defined.")\n
  raise ValidationFailed, (msg,)\n
\n
# Check getBaobabSource and getBaobabDestination\n
#transaction.Base_checkBaobabSourceAndDestination()\n
\n
\n
# check we don\'t change of user\n
transaction.Baobab_checkSameUserVault(destination)\n
\n
lettering = transaction.getGroupingReference()\n
\n
if lettering is None:\n
  msg = Message(domain=\'ui\', message=\'No lettering defined.\')\n
  raise ValidationFailed, (msg,)\n
\n
if destination is None:\n
  msg = Message(domain=\'ui\', message=\'No counter defined.\')\n
  raise ValidationFailed, (msg,)\n
\n
\n
\n
# Get price and total_price.\n
price = transaction.getSourceTotalAssetPrice()\n
cash_detail = transaction.getTotalPrice(portal_type = [\'Cash Delivery Line\', \'Cash Delivery Cell\'], fast=0)\n
\n
if price != cash_detail:\n
  msg = Message(domain="ui", message="Amount differs from input.")\n
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
