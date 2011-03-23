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

from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
from Products.ERP5Type.Message import Message\n
\n
counter_site = context.getSource()\n
# check we don\'t change of user\n
context.Baobab_checkSameUserVault(counter_site)\n
# check that we are in the good accounting date\n
context.Baobab_checkCounterDateOpen(site=counter_site,\n
  date=context.getStartDate())\n
# check that the counter is open\n
context.Baobab_checkCounterOpened(counter_site)\n
\n
if is_currency_sale:\n
  foreign_currency_portal_type = outgoing_portal_type\n
  default_currency_portal_type = incoming_portal_type\n
  total_quantity = context.CurrencySale_getQuantity()\n
else:\n
  foreign_currency_portal_type = incoming_portal_type\n
  default_currency_portal_type = outgoing_portal_type\n
  total_quantity = context.CurrencyPurchase_getQuantity()\n
\n
# check if an exchange rate is defined\n
if total_quantity is None:\n
  raise ValidationFailed, (Message(domain=\'ui\',\n
    message="No exchange rate defined for this currency at document date."))\n
\n
# check resource on currency fastinput\n
doc_resource = context.getResource()\n
for line in context.contentValues(portal_type=foreign_currency_portal_type):\n
  if line.getResourceValue().getPriceCurrency() != doc_resource:\n
    raise ValidationFailed, (Message(domain="ui",\n
      message="Resource defined on document is different from currency cash."), )\n
\n
# check outgoing amount\n
if is_currency_sale:\n
  amount = context.getSourceTotalAssetPrice()\n
else:\n
  amount = context.getQuantity()\n
if amount is None or amount <= 0:\n
  msg = Message(domain="ui", message="Amount is not valid.")\n
  raise ValidationFailed, (msg, )\n
\n
# Reverse error messages in cash of currency purchase\n
default_msg = "Received amount is different from input cash."\n
foreign_msg = "Return amount is different from output cash"\n
if not is_currency_sale:\n
  (default_msg, foreign_msg) = (foreign_msg, default_msg)\n
\n
# Check default currency amount consistency\n
if context.getTotalPrice(portal_type=[default_currency_portal_type,\n
    \'Cash Delivery Cell\'], fast=0) != context.getQuantity():\n
  raise ValidationFailed, (Message(domain="ui", message=default_msg), )\n
\n
# Check foreign currency amount consistency\n
if context.getTotalPrice(portal_type=[foreign_currency_portal_type,\n
    \'Cash Delivery Cell\'], fast=0) != context.getSourceTotalAssetPrice():\n
  raise ValidationFailed, (Message(domain="ui", message=foreign_msg), )\n
\n
# Check outgoing inventory\n
resource_one = context.CashDelivery_checkCounterInventory(\n
  portal_type=outgoing_portal_type)\n
if resource_one == 2:\n
  raise ValidationFailed, (Message(domain="ui", message="No Resource."), )\n
elif resource_one == 1:\n
  raise ValidationFailed, (Message(domain="ui",\n
    message="Insufficient balance"), )\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>incoming_portal_type, outgoing_portal_type, is_currency_sale</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CurrencySaleOrPurchase_validateVaultBalance</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
