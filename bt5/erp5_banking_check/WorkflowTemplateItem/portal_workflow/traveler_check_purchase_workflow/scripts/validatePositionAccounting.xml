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
transaction = state_change[\'object\']\n
\n
date = transaction.getStartDate()\n
source = transaction.getSource(None)\n
if source is None:\n
  msg = Message(domain=\'ui\', message=\'No counter defined.\')\n
  raise ValidationFailed, (msg,)\n
\n
# check we don\'t change of user\n
transaction.Baobab_checkSameUserVault(source)\n
\n
# check we are in an opened accounting day\n
transaction.Baobab_checkCounterDateOpen(site=source, date=date)\n
\n
context.Baobab_checkCounterOpened(source)\n
\n
# First we have to look if we have some checks with some prices,\n
# if so, this means that we are saling such kinds of check, thus\n
# we must change the position of the customer account\n
movement_list = transaction.getMovementList()\n
total_credit = 0\n
for movement in movement_list:\n
  aggregate_value_list = movement.getAggregateValueList()\n
  for item in aggregate_value_list:\n
    if item.getPortalType()==\'Check\':\n
      if item.getSimulationState()!=\'confirmed\':\n
        msg = Message(domain = "ui", message="Sorry, one traveler check was not sale yet")\n
        raise ValidationFailed, (msg,)\n
      if item.getPrice() is not None:\n
        # then we must calculate the exchange value at the\n
        # time where the item was first delivered\n
        category_list = movement.getCategoryList()\n
        base_price = transaction.CurrencyExchange_getExchangeRateList(\n
                                    from_currency=item.getPriceCurrency(),\n
                                    to_currency=\'currency_module/%s\' % context.Baobab_getPortalReferenceCurrencyID(),\n
                                    currency_exchange_type=\'transfer\',\n
                                    start_date=item.getStartDate())[0]\n
        if base_price is None:\n
          msg = Message(domain = "ui", message="Sorry, no valid price was found for this currency")\n
          raise ValidationFailed, (msg,)\n
        total_credit += base_price*item.getPrice()\n
      else:\n
        msg = Message(domain = "ui", message="Sorry, the price was not defined on some traveler checks")\n
        raise ValidationFailed, (msg,)\n
\n
if total_credit>0:\n
  total_credit = round(total_credit,0)\n
  # Source and destination will be updated automaticaly based on the category of bank account\n
  # The default account chosen should act as some kind of *temp* account or *parent* account\n
  movement = transaction.get(\'movement\',None)\n
  if movement is None:\n
    movement = transaction.newContent(portal_type=\'Banking Operation Line\',\n
                           id=\'movement\',\n
                           source=\'account_module/bank_account\', # Set default source\n
                           destination=\'account_module/bank_account\', # Set default destination\n
                           )\n
  movement.setSourceCredit(total_credit)\n
  transaction.setSourceTotalAssetPrice(total_credit)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>validatePositionAccounting</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
