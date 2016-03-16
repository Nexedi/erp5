from Products.ERP5Type.Document import newTempBase

if reference == []:
  return []
elif reference is None:
  account_list = [context]
else:
  account_list = context.BankAccount_getReportInformationList(reference=reference, 
                              force_one_account=force_one_account)

# Build the common inventory dict
params = {}
if from_date is not None:
  params['from_date'] = from_date
if at_date is not None:
  params['at_date'] = at_date

account_dict = {}
for account in account_list:
  account_dict[account.getUid()] = account

account_uids = account_dict.keys()
resource_uid = context.currency_module[context.Baobab_getPortalReferenceCurrencyID()].getUid()

inv_account_dict = {}
# Set empty dictionnary for each account
for account_uid in account_uids:
  account = account_dict[account_uid]
  parent_value = account.getParentValue()
  account_state = account.getValidationState()
  if account_state == 'closed':
    closed_date = DateTime(account.Base_getWorkflowHistory()['bank_account_workflow']['item_list'][0][-1]).Date()
  else:
    closed_date = None
  if parent_value.getPortalType() == 'Organisation':
    parent_activity = parent_value.getActivity()
  else:
    parent_activity = None
  inv_account_dict[account_uid] = {
    'state_title': account_state,
    'closed_date': closed_date,
    'account_reference': account.getReference(),
    'internal_bank_account_number': account.getInternalBankAccountNumber(),
    'state': account.getValidationState(),
    'activity': parent_activity,
    'account_owner': parent_value.getTitle(),
    'currency_title': account.getPriceCurrencyTitle(),
    'bic_code': account.getBicCode(None),
    'transaction_list': [],
  }

# Current inventory
if current_inventory:
  current_available_inventory_list = context.portal_simulation.getCurrentInventoryList(
    payment_uid = account_uids,
    resource_uid = resource_uid,
    group_by_payment = 1,
    **params
    )
  for inv in current_available_inventory_list:
    inv_account_dict[inv.payment_uid]["current"] = inv.total_quantity

# Available inventory
if available_inventory:
  available_inventory_list = context.portal_simulation.getAvailableInventoryList(
    payment_uid = account_uids,
    resource_uid = resource_uid,
    group_by_payment = 1,
    **params
    )
  for inv in available_inventory_list:
    inv_account_dict[inv.payment_uid]["available"] = inv.total_quantity

# Future inventory
if future_inventory:
  future_inventory_list = context.portal_simulation.getFutureInventoryList(
    payment_uid = account_uids,
    resource_uid = resource_uid,
    group_by_payment = 1,
    **params
    )
  for inv in future_inventory_list:
    inv_account_dict[inv.payment_uid]["future"] = inv.total_quantity


final_inventory_list = []
portal = account.getPortalObject()
i = 0

if transaction_list:
  inventory_list = context.portal_simulation.getCurrentInventoryList(
    payment_uid = account_uids,
    resource_uid = resource_uid,
    **params
    )

  for inventory in inventory_list:
    tmp_dict = {}

    # Specific to each movement
    movement = portal.restrictedTraverse(inventory.path)
    delivery = movement.getExplanationValue()
    document_reference = delivery.getSourceReference()
    if document_reference is None:
      document_reference = ''
    tmp_dict['document_reference'] = document_reference
    total_price = inventory.total_quantity
    tmp_dict['total_price'] = total_price
    cancellation_amount = movement.isCancellationAmount()
    tmp_dict['cancellation_amount'] = cancellation_amount
    tmp_dict['debit'] = None
    tmp_dict['credit'] = None
    if total_price is not None:
      if not cancellation_amount:
        if total_price >= 0:
          tmp_dict['debit'] = total_price
        elif total_price < 0:
          tmp_dict['credit'] = - total_price
      else:
        if total_price < 0:
          tmp_dict['debit'] = total_price
        elif total_price >= 0:
          tmp_dict['credit'] = - total_price

    description = delivery.getDescription()
    if description is None:
      description = ''
    tmp_dict['description'] = description
    tmp_dict['start_date'] = inventory.date
    tmp_dict['module_title'] = delivery.getParentValue().getTranslatedTitle()

    # Common to bank account
    acc_dict = inv_account_dict[inventory.payment_uid]
    acc_dict['transaction_list'].append(newTempBase(account, "new_%03i" % i, **tmp_dict))
    i += 1

def sort_date(a,b):
#   result = cmp(a.account_reference,b.account_reference)
#   if result == 0:
  return cmp(a.start_date,b.start_date)
#   return result

for act_info in inv_account_dict.values():
  act_info['transaction_list'].sort(sort_date)
  

return inv_account_dict.values()
