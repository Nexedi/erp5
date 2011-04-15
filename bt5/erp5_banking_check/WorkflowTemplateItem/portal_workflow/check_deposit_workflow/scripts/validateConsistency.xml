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
from Products.ERP5Type.DateUtils import getIntervalBetweenDates\n
\n
transaction = state_change[\'object\']\n
\n
site = transaction.getSite()\n
date = transaction.getStartDate()\n
transaction.Baobab_checkAccountingDateOpen(site=site, date=date)\n
\n
# Check we don\'t defined accounting code and account\n
if transaction.getDestinationSection() not in ("", None) and \\\n
       transaction.getDestinationPayment() not in ("", None):\n
  msg = Message(domain=\'ui\', message="You can\'t defined both account and accounting code.")\n
  raise ValidationFailed, (msg,)\n
  \n
if transaction.getDestinationSection() in ("", None) and \\\n
       transaction.getDestinationPayment() in ("", None):\n
  msg = Message(domain=\'ui\', message="You must defined an account or and accounting code as destination.")\n
  raise ValidationFailed, (msg,)\n
\n
if transaction.getSite() in ("", None):\n
  msg = Message(domain=\'ui\', message="You must defined site on document.")\n
  raise ValidationFailed, (msg,)\n
\n
# Check the amount.\n
price = transaction.getSourceTotalAssetPrice()\n
if price is None or price <= 0:\n
  msg = Message(domain=\'ui\', message=\'Amount is not valid.\')\n
  raise ValidationFailed, (msg,)\n
\n
# Check the bank account.\n
destination_bank_account = transaction.getDestinationPaymentValue()\n
if destination_bank_account is not None:\n
  if destination_bank_account.getValidationState() != \'valid\':\n
    msg = Message(domain=\'ui\', message=\'Destination bank account is not valid.\')\n
    raise ValidationFailed, (msg,)\n
\n
# Check if the total price is equal to the total asset price.\n
if transaction.getTotalPrice(fast=0, portal_type = \'Check Operation Line\') != transaction.getSourceTotalAssetPrice():\n
  msg = Message(domain=\'ui\', message="Total price doesn\'t match.")\n
  raise ValidationFailed, (msg,)\n
\n
seen_check_dict = {}\n
\n
is_check_less = transaction.isCheckLess()\n
\n
# Check each check operation line.\n
for check_operation_line in transaction.contentValues(filter = {\'portal_type\' : \'Check Operation Line\'}):\n
\n
  if check_operation_line.getDescription() in (None, \'\'):\n
    msg = Message(domain=\'ui\', message=\'The description is not defined on line $line.\'\n
                  , mapping={"line" : check_operation_line.getId()})\n
    raise ValidationFailed, (msg,)\n
\n
  source_bank_account = check_operation_line.getSourcePaymentValue()\n
  if source_bank_account is None:\n
    msg = Message(domain=\'ui\', message=\'Bank account not defined on line $line.\'\n
                  , mapping={"line" : check_operation_line.getId()})\n
    raise ValidationFailed, (msg,)\n
\n
  check_number = check_operation_line.getAggregateFreeText()\n
  check_type = check_operation_line.getAggregateResource()\n
  if is_check_less:\n
    if check_number:\n
      msg = Message(domain=\'ui\', message=\'Check is defined on line $line.\'\n
                    , mapping={"line" : check_operation_line.getId()})\n
      raise ValidationFailed, (msg,)\n
\n
    if check_type is not None:\n
      msg = Message(domain=\'ui\', message=\'Check type is defined on line $line.\'\n
                    , mapping={"line" : check_operation_line.getId()})\n
      raise ValidationFailed, (msg,)\n
  else:\n
    if not check_number:\n
      msg = Message(domain=\'ui\', message=\'Check is not defined on line $line.\'\n
                    , mapping={"line" : check_operation_line.getId()})\n
      raise ValidationFailed, (msg,)\n
\n
    if check_type is None:\n
      msg = Message(domain=\'ui\', message=\'Check type is not defined on line $line.\'\n
                    , mapping={"line" : check_operation_line.getId()})\n
      raise ValidationFailed, (msg,)\n
\n
    seen_check_dict_key = (source_bank_account, check_type, check_number)\n
    seen_check = seen_check_dict.get(seen_check_dict_key)\n
    if seen_check is not None:\n
      msg = Message(domain=\'ui\', message=\'Check on line $line is already used on line $oldline.\'\n
                    , mapping={"line" : check_operation_line.getId(), "oldline": seen_check})\n
      raise ValidationFailed, (msg,)\n
    seen_check_dict[seen_check_dict_key] = check_operation_line.getId()\n
\n
    # Test check is valid based on date\n
    transaction.Check_checkIntervalBetweenDate(resource=check_operation_line.getAggregateResourceValue(),\n
                                               start_date=check_operation_line.getIssueDate(),\n
                                               stop_date=check_operation_line.getStopDate(),\n
                                               check_nb=check_operation_line.getAggregateFreeText())\n
    check = transaction.Base_checkCheck(bank_account=source_bank_account, reference=check_number,\n
                                resource=check_type)\n
    if check_operation_line.getAggregate() != check.getRelativeUrl():\n
      check_operation_line.edit(aggregate=check.getRelativeUrl())\n


]]></string> </value>
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
            <value> <string>validateConsistency</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
