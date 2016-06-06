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

from Products.ERP5Type.Document import newTempBase\n
\n
if reference == []:\n
  return []\n
elif reference is None:\n
  account_list = [context]\n
else:\n
  account_list = context.BankAccount_getReportInformationList(reference=reference, \n
                              force_one_account=force_one_account)\n
\n
# Build the common inventory dict\n
params = {}\n
if from_date is not None:\n
  params[\'from_date\'] = from_date\n
if at_date is not None:\n
  params[\'at_date\'] = at_date\n
\n
account_dict = {}\n
for account in account_list:\n
  account_dict[account.getUid()] = account\n
\n
account_uids = account_dict.keys()\n
resource_uid = context.currency_module[context.Baobab_getPortalReferenceCurrencyID()].getUid()\n
\n
inv_account_dict = {}\n
# Set empty dictionnary for each account\n
for account_uid in account_uids:\n
  account = account_dict[account_uid]\n
  parent_value = account.getParentValue()\n
  account_state = account.getValidationState()\n
  if account_state == \'closed\':\n
    closed_date = DateTime(account.Base_getWorkflowHistory()[\'bank_account_workflow\'][\'item_list\'][0][-1]).Date()\n
  else:\n
    closed_date = None\n
  if parent_value.getPortalType() == \'Organisation\':\n
    parent_activity = parent_value.getActivity()\n
  else:\n
    parent_activity = None\n
  inv_account_dict[account_uid] = {\n
    \'state_title\': account_state,\n
    \'closed_date\': closed_date,\n
    \'account_reference\': account.getReference(),\n
    \'internal_bank_account_number\': account.getInternalBankAccountNumber(),\n
    \'state\': account.getValidationState(),\n
    \'activity\': parent_activity,\n
    \'account_owner\': parent_value.getTitle(),\n
    \'currency_title\': account.getPriceCurrencyTitle(),\n
    \'bic_code\': account.getBicCode(None),\n
    \'transaction_list\': [],\n
  }\n
\n
# Current inventory\n
if current_inventory:\n
  current_available_inventory_list = context.portal_simulation.getCurrentInventoryList(\n
    payment_uid = account_uids,\n
    resource_uid = resource_uid,\n
    group_by_payment = 1,\n
    **params\n
    )\n
  for inv in current_available_inventory_list:\n
    inv_account_dict[inv.payment_uid]["current"] = inv.total_quantity\n
\n
# Available inventory\n
if available_inventory:\n
  available_inventory_list = context.portal_simulation.getAvailableInventoryList(\n
    payment_uid = account_uids,\n
    resource_uid = resource_uid,\n
    group_by_payment = 1,\n
    **params\n
    )\n
  for inv in available_inventory_list:\n
    inv_account_dict[inv.payment_uid]["available"] = inv.total_quantity\n
\n
# Future inventory\n
if future_inventory:\n
  future_inventory_list = context.portal_simulation.getFutureInventoryList(\n
    payment_uid = account_uids,\n
    resource_uid = resource_uid,\n
    group_by_payment = 1,\n
    **params\n
    )\n
  for inv in future_inventory_list:\n
    inv_account_dict[inv.payment_uid]["future"] = inv.total_quantity\n
\n
\n
final_inventory_list = []\n
portal = account.getPortalObject()\n
i = 0\n
\n
if transaction_list:\n
  inventory_list = context.portal_simulation.getCurrentInventoryList(\n
    payment_uid = account_uids,\n
    resource_uid = resource_uid,\n
    **params\n
    )\n
\n
  for inventory in inventory_list:\n
    tmp_dict = {}\n
\n
    # Specific to each movement\n
    movement = portal.restrictedTraverse(inventory.path)\n
    delivery = movement.getExplanationValue()\n
    document_reference = delivery.getSourceReference()\n
    if document_reference is None:\n
      document_reference = \'\'\n
    tmp_dict[\'document_reference\'] = document_reference\n
    total_price = inventory.total_quantity\n
    tmp_dict[\'total_price\'] = total_price\n
    cancellation_amount = movement.isCancellationAmount()\n
    tmp_dict[\'cancellation_amount\'] = cancellation_amount\n
    tmp_dict[\'debit\'] = None\n
    tmp_dict[\'credit\'] = None\n
    if total_price is not None:\n
      if not cancellation_amount:\n
        if total_price >= 0:\n
          tmp_dict[\'debit\'] = total_price\n
        elif total_price < 0:\n
          tmp_dict[\'credit\'] = - total_price\n
      else:\n
        if total_price < 0:\n
          tmp_dict[\'debit\'] = total_price\n
        elif total_price >= 0:\n
          tmp_dict[\'credit\'] = - total_price\n
\n
    description = delivery.getDescription()\n
    if description is None:\n
      description = \'\'\n
    tmp_dict[\'description\'] = description\n
    tmp_dict[\'start_date\'] = inventory.date\n
    tmp_dict[\'module_title\'] = delivery.getParentValue().getTranslatedTitle()\n
\n
    # Common to bank account\n
    acc_dict = inv_account_dict[inventory.payment_uid]\n
    acc_dict[\'transaction_list\'].append(newTempBase(account, "new_%03i" % i, **tmp_dict))\n
    i += 1\n
\n
def sort_date(a,b):\n
#   result = cmp(a.account_reference,b.account_reference)\n
#   if result == 0:\n
  return cmp(a.start_date,b.start_date)\n
#   return result\n
\n
for act_info in inv_account_dict.values():\n
  act_info[\'transaction_list\'].sort(sort_date)\n
  \n
\n
return inv_account_dict.values()\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>from_date=None, at_date=None, reference=None, current_inventory=0, available_inventory=0, future_inventory=0, transaction_list=0, force_one_account=0</string> </value>
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
            <value> <string>BankAccount_getReportTransactionList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
