"""Creates a balance transaction to open the next period.

"""
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery

portal = context.getPortalObject()
Base_translateString = portal.Base_translateString

precision_cache = {}
def roundCurrency(value, resource_relative_url):
  if resource_relative_url not in precision_cache:
    qty_precision = portal.restrictedTraverse(
                        resource_relative_url).getQuantityPrecision()
    precision_cache[resource_relative_url] = qty_precision
  qty_precision = precision_cache[resource_relative_url]
  return round(value, qty_precision)

# This tag is checked in accounting period workflow
activity_tag = 'BalanceTransactionCreation'

at_date = context.getStopDate()
assert at_date

section = context.getParentValue()
section_currency = section.getPriceCurrency()
section_currency_precision = section.getPriceCurrencyValue().getQuantityPrecision()


# we have two distinct cases:
#  * child organisations does not have accounting periods, we create balance
#    transactions for each of those sections.
#  * child organisations have valid accounting periods, we will create balance
#    transactions for the sections when we close their respective periods

def isIndenpendantSection(section):
  for ap in section.contentValues(
              portal_type='Accounting Period',
              checked_permission='View'):
    if ap.getSimulationState() in ('started', 'stopped', 'delivered'):
      return True
  return False

def getDependantSectionList(group, main_section):
  section_list = []
  recurse = True
  for section in group.getGroupRelatedValueList(
                            portal_type='Organisation',
                            strict_membership=True,
                            checked_permission='View'):
    if section != main_section:
      if isIndenpendantSection(section):
        recurse = False
      else:
        section_list.append(section)
  if recurse:
    for subgroup in group.contentValues():
      section_list.extend(getDependantSectionList(subgroup, main_section))

  return section_list

group_value = section.getGroupValue()
section_list = [section]
if group_value is not None:
  section_list.extend(getDependantSectionList(group_value, section))

ledger_list = portal.portal_categories.ledger.getCategoryChildValueList(is_self_excluded=1) + [None,]

def createBalanceTransaction(section, ledger=None):
  balance_date = at_date + 1
  # We discard hours, minutes and seconds and at the same time, make sure the date
  # is in its "normal timezone". For example, when at_date is the day of a dailight saving
  # time switch, we want this date to be in the new timezone.
  balance_date = DateTime(balance_date.year(), balance_date.month(), balance_date.day())
  return portal.accounting_module.newContent(
                          portal_type='Balance Transaction',
                          ledger=ledger,
                          start_date=balance_date,
                          title=context.getTitle() or Base_translateString('Balance Transaction'),
                          destination_section_value=section,
                          resource=section_currency,
                          causality_value=context)

getInventoryList = portal.portal_simulation.getInventoryList

with context.defaultActivateParameterDict({'tag': activity_tag}, placeless=True):
  # List ledgers on which there are movements
  inventory_ledger_uid_list = [inventory.ledger_uid for inventory \
    in getInventoryList(at_date=at_date.latestTime(),
                        portal_type=portal.getPortalAccountingMovementTypeList(),
                        group_by_ledger=True)]

  for ledger in ledger_list:

    # If there are no movements within this ledger, we can
    # directly go to another
    if ledger is None and None not in inventory_ledger_uid_list:
      continue
    elif ledger is not None and ledger.getUid() not in inventory_ledger_uid_list:
      continue

    if ledger is not None:
      ledger_uid = ledger.getUid()
      ledger_url = ledger.getCategoryRelativeUrl()
    else:
      ledger_uid = SimpleQuery(ledger_uid=None)
      ledger_url = ''

    for section in section_list:
      section_uid = section.getUid()
      balance_transaction = None

      group_by_node_node_category_list = []
      group_by_mirror_section_node_category_list = []
      group_by_payment_node_category_list = []
      profit_and_loss_node_category_list = []

      node_category_list = portal.portal_categories\
                  .account_type.getCategoryChildValueList()
      for node_category in node_category_list:
        node_category_url = node_category.getRelativeUrl()
        if node_category_url in (
            'account_type/asset/cash/bank',):
          group_by_payment_node_category_list.append(node_category_url)
        elif node_category_url in (
            'account_type/asset/receivable',
            'account_type/liability/payable'):
          group_by_mirror_section_node_category_list.append(node_category_url)
        elif node_category.isMemberOf('account_type/income') or \
             node_category.isMemberOf('account_type/expense'):
          profit_and_loss_node_category_list.append(node_category_url)
        else:
          group_by_node_node_category_list.append(node_category_url)

      inventory_param_dict = dict(section_uid=section_uid,
                                  simulation_state=('delivered',),
                                  precision=section_currency_precision,
                                  portal_type=portal.getPortalAccountingMovementTypeList(),
                                  at_date=at_date.latestTime(),
                                  ledger_uid=ledger_uid)

      # Calculate the sum of profit and loss accounts balances for that period.
      # This must match the difference between assets, liability and equity accounts.
      profit_and_loss_accounts_balance = portal.portal_simulation.getInventoryAssetPrice(
        from_date=context.getStartDate(),
        node_category_strict_membership=profit_and_loss_node_category_list,
        **inventory_param_dict)
      selected_profit_and_loss_account_balance = portal.portal_simulation.getInventoryAssetPrice(
        node=profit_and_loss_account,
        resource=section_currency,
        **inventory_param_dict)

      section_currency_uid = context.getParentValue().getPriceCurrencyUid()

      profit_and_loss_quantity = 0
      line_count = 0

      for inventory in getInventoryList(
              node_category_strict_membership=group_by_node_node_category_list,
              group_by_node=1,
              group_by_resource=1,
              **inventory_param_dict):

        total_price = roundCurrency(inventory.total_price or 0, section_currency)
        quantity = roundCurrency(inventory.total_quantity or 0,
                                 inventory.resource_relative_url)

        if not total_price and not quantity:
          continue

        line_count += 1
        if inventory.resource_uid != section_currency_uid:
          profit_and_loss_quantity += total_price

          if balance_transaction is None:
            balance_transaction = createBalanceTransaction(section, ledger_url)
          balance_transaction.newContent(
              id='%03d' % line_count,
              portal_type='Balance Transaction Line',
              destination=inventory.node_relative_url,
              resource=inventory.resource_relative_url,
              quantity=quantity,
              destination_total_asset_price=total_price)
        else:
          if total_price != quantity:
            # If this fail for you, your accounting doesn't use currencies with
            # consistency
            raise ValueError('Different price: %s != %s ' % (
                              total_price, quantity))

          if inventory.node_relative_url != profit_and_loss_account:
            profit_and_loss_quantity += total_price
            if balance_transaction is None:
              balance_transaction = createBalanceTransaction(section, ledger_url)
            balance_transaction.newContent(
              id='%03d' % line_count,
              portal_type='Balance Transaction Line',
              destination=inventory.node_relative_url,
              quantity=total_price)


      for inventory in getInventoryList(
              node_category_strict_membership=group_by_mirror_section_node_category_list,
              group_by_node=1,
              group_by_mirror_section=1,
              group_by_resource=1,
              **inventory_param_dict):

        total_price = roundCurrency(inventory.total_price or 0, section_currency)
        quantity = roundCurrency(inventory.total_quantity or 0,
                                 inventory.resource_relative_url)

        if not total_price and not quantity:
          continue
        profit_and_loss_quantity += total_price
        line_count += 1

        if inventory.resource_uid != section_currency_uid:
          if balance_transaction is None:
            balance_transaction = createBalanceTransaction(section, ledger_url)
          balance_transaction.newContent(
            id='%03d' % line_count,
            portal_type='Balance Transaction Line',
            destination=inventory.node_relative_url,
            source_section_uid=inventory.mirror_section_uid,
            resource=inventory.resource_relative_url,
            quantity=quantity,
            destination_total_asset_price=total_price)
        else:
          if total_price != quantity:
            raise ValueError('Different price: %s != %s ' % (
                              total_price, quantity))
          if balance_transaction is None:
            balance_transaction = createBalanceTransaction(section, ledger_url)
          balance_transaction.newContent(
            id='%03d' % line_count,
            portal_type='Balance Transaction Line',
            destination=inventory.node_relative_url,
            source_section_uid=inventory.mirror_section_uid,
            quantity=total_price)


      for inventory in getInventoryList(
              node_category_strict_membership=group_by_payment_node_category_list,
              group_by_node=1,
              group_by_payment=1,
              group_by_resource=1,
              **inventory_param_dict):

        total_price = roundCurrency(inventory.total_price or 0, section_currency)
        quantity = roundCurrency(inventory.total_quantity or 0,
                                 inventory.resource_relative_url)

        if not total_price and not quantity:
          continue
        profit_and_loss_quantity += total_price

        line_count += 1

        if inventory.resource_uid != section_currency_uid:
          if balance_transaction is None:
            balance_transaction = createBalanceTransaction(section, ledger_url)
          balance_transaction.newContent(
            id='%03d' % line_count,
            portal_type='Balance Transaction Line',
            destination=inventory.node_relative_url,
            resource=inventory.resource_relative_url,
            quantity=quantity,
            destination_payment_uid=inventory.payment_uid,
            destination_total_asset_price=total_price)
        else:
          if total_price != quantity:
            raise ValueError('Different price: %s != %s ' % (
                              total_price, quantity))
          if balance_transaction is None:
            balance_transaction = createBalanceTransaction(section, ledger_url)
          balance_transaction.newContent(
            id='%03d' % line_count,
            portal_type='Balance Transaction Line',
            destination=inventory.node_relative_url,
            destination_payment_uid=inventory.payment_uid,
            quantity=total_price)

      if balance_transaction is None:
        # we did not have any transaction for this section

        # One possible corner case is that we have only transactions that brings
        # the balance of all balance sheets accounts to 0. In this case we want to
        # create a balance transaction that notes that the current balance of profit
        # and loss account is 0, so that the delta gets indexed.
        if profit_and_loss_accounts_balance:
          balance_transaction = createBalanceTransaction(section, ledger_url)
          balance_transaction.newContent(
                portal_type='Balance Transaction Line',
                destination=profit_and_loss_account,
                quantity=0)
          balance_transaction.stop()
          balance_transaction.deliver()
        continue

      assert roundCurrency(profit_and_loss_accounts_balance, section_currency) == roundCurrency(
           - roundCurrency(selected_profit_and_loss_account_balance, section_currency)
           - roundCurrency(profit_and_loss_quantity, section_currency), section_currency)

      # If profit_and_loss_quantity equals 0 then we are on a
      # ledger which no accounting transactions are member of
      if profit_and_loss_quantity != 0.:
        # add a final line for p&l
        balance_transaction.newContent(
                  id='%03d' % (line_count + 1),
                  portal_type='Balance Transaction Line',
                  destination=profit_and_loss_account,
                  quantity=-profit_and_loss_quantity)

        # and go to delivered state directly (the user is not supposed to edit this document)
        balance_transaction.stop()
        balance_transaction.deliver()

# make sure this Accounting Period has an activity pending during the indexing
# of the balance transaction.
context.activate(after_tag=activity_tag).getTitle()
