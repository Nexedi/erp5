"""Returns the difference between the original total payable price of this
invoice and all payments that have been made on this invoice.
For this, we use both causality relation between transactions and grouping
reference for lines.

If `detailed` argument is set to a true value, instead of returning the price
as a float value, it returns a mapping (node, mirror_section) -> total_price.

The `at_date` paremeter is when you want to know the remaining amount at a
particuliar date. This simply ignores related payments or transactions after
this date.

The `account_id` parameter can be use to filter receivable / payable lines to a
specific account.

The `simulation_state` parameter is a list that can be used to take into account
only transactions in those states. By default it will use all but 'draft',
, 'rejected', 'cancelled' and 'deleted'.

The `mirror_section_relative_url` parameter must be passed explicitly if the
context invoice has multiple sections.

If `quantity` parameter is true, this script will return the quantities in the
original transaction currency. If currencies on this invoice and the related
payments are not consistent, a ValueError is raised.
"""
portal = context.getPortalObject()
total_payable_price_per_node_section = {}

if simulation_state is None:
  state_list = [x[1] for x in context.ERP5Site_getWorkflowStateItemList(
            portal_type='Accounting Transaction', state_var='simulation_state')]
  simulation_state = [x for x in state_list
                      if x not in ('draft', 'cancelled', 'deleted', 'rejected')]

# remember payable / receivable lines in context.
accounts_in_context = []

if isinstance(account_id, str):
  account_id = [account_id]

accounting_transaction_type_list = [x for x in
            portal.getPortalAccountingTransactionTypeList()
              if x != 'Balance Transfer Transaction']

def getIsSourceMovementItemList(invoice):
  """Returns all movements inside the invoice, and a flag to know if we are
  source on this movement
  Handle the (very ad hoc) case of Balance Transfer Transactions
  """
  is_source = invoice.AccountingTransaction_isSourceView()
  movement_item_list = [(is_source, m) for m in invoice.getMovementList(
          portal_type=portal.getPortalAccountingMovementTypeList())]
  for btt in context.getCausalityRelatedValueList(
                        portal_type='Balance Transfer Transaction',
                        checked_permission='Access contents information'):
    if simulation_state and btt.getSimulationState() not in simulation_state:
      continue
    btt_is_source = btt.AccountingTransaction_isSourceView()
    for btt_movement in btt.getMovementList(
                  portal_type=portal.getPortalAccountingMovementTypeList()):
      movement_item_list.append((btt_is_source, btt_movement))

  return movement_item_list


invoice_currency = context.getResource()
# calculate the total price of this invoice (according to accounting
# transaction lines)
for is_source, line in getIsSourceMovementItemList(context):

  if is_source:
    node_value = line.getSourceValue(portal_type='Account')
    mirror_section = line.getDestinationSection()
    if quantity:
      amount = -line.getQuantity()
    else:
      amount = line.getSourceInventoriatedTotalAssetPrice() or 0
  else:
    node_value = line.getDestinationValue(portal_type='Account')
    mirror_section = line.getSourceSection()
    if quantity:
      amount = line.getQuantity()
    else:
      amount = line.getDestinationInventoriatedTotalAssetPrice() or 0

  if at_date is None and line.getGroupingReference():
    continue

  if node_value is not None:
    if account_id is not None and node_value.getId() not in account_id:
      continue
    if account_id is None and node_value.getAccountTypeId() not in ('payable', 'receivable'):
      continue
    key = (node_value.getRelativeUrl(), mirror_section)
    total_payable_price_per_node_section[key] =\
          total_payable_price_per_node_section.get(key, 0) + amount
    accounts_in_context.append(node_value)


related_transaction_list = context.getCausalityRelatedValueList(
                          portal_type=accounting_transaction_type_list,
                          checked_permission='Access contents information')

# substract all causalities
for related_transaction in related_transaction_list:
  if related_transaction.getSimulationState() not in simulation_state:
    continue
  if related_transaction.getProperty('origin_id') == 'MAJO':
    continue

  # if we have a payment related to multiple invoices, we cannot say the
  # remaining price on those invoices.
  for other_invoice in [ tr for tr in related_transaction.getCausalityValueList(
                         portal_type=accounting_transaction_type_list)
                         if tr not in related_transaction_list + [context]]:
    other_invoice_is_source = \
                    other_invoice.AccountingTransaction_isSourceView()
    for other_line in other_invoice.getMovementList(
            portal_type=portal.getPortalAccountingMovementTypeList()):
      if other_line.getGroupingReference():
        continue
      if other_invoice_is_source:
        other_invoice_line_account = other_line.getSourceValue()
        other_invoice_line_mirror_section = other_line.getDestinationSection()
      else:
        other_invoice_line_account = other_line.getDestinationValue()
        other_invoice_line_mirror_section = other_line.getSourceSection()

      if other_invoice_line_account in accounts_in_context:
        # unless this line is for another mirror_section, we cannot calculate
        if mirror_section_relative_url is None or \
              other_invoice_line_mirror_section == mirror_section_relative_url:
          raise ValueError('Unable to calculate %s' % context.getPath())

  related_transaction_is_source = related_transaction.\
                                        AccountingTransaction_isSourceView()
  for line in related_transaction.getMovementList(
            portal_type=portal.getPortalAccountingMovementTypeList()):

    if at_date is None and line.getGroupingReference():
      continue

    if quantity:
      if line.getResource() != invoice_currency:
        raise ValueError("Unable to calculate"
        ", related transaction %s uses different currency" %
          line.getRelativeUrl())

    if related_transaction_is_source:
      node_value = line.getSourceValue(portal_type='Account')
      mirror_section = line.getDestinationSection()
      if quantity:
        amount = -line.getQuantity()
      else:
        amount = line.getSourceInventoriatedTotalAssetPrice() or 0
      date = line.getStartDate().earliestTime()
    else:
      node_value = line.getDestinationValue(portal_type='Account')
      mirror_section = line.getSourceSection()
      if quantity:
        amount = line.getQuantity()
      else:
        amount = line.getDestinationInventoriatedTotalAssetPrice() or 0
      date = line.getStopDate().earliestTime()

    if node_value is not None:
      if account_id is not None and node_value.getId() not in account_id:
        continue
      if account_id is None and node_value.getAccountTypeId() not in ('payable', 'receivable'):
        continue
      if at_date and date > at_date:
        continue
      if node_value in accounts_in_context:
        key = (node_value.getRelativeUrl(), mirror_section)
        total_payable_price_per_node_section[key] =\
            total_payable_price_per_node_section.get(key, 0) + amount

if detailed:
  return total_payable_price_per_node_section
else:
  if mirror_section_relative_url:
    total_amount = 0
    for (node, mirror_section), amount in total_payable_price_per_node_section.items(): # pylint: disable=unused-variable
      if mirror_section == mirror_section_relative_url:
        total_amount += amount
    return total_amount
  return sum(total_payable_price_per_node_section.values())
