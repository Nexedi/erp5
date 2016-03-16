from Products.ZSQLCatalog.SQLCatalog import Query
from Products.PythonScripts.standard import Object
from ZTUtils import LazyFilter

request = container.REQUEST
portal = context.getPortalObject()
getInventoryList = portal.portal_simulation.getInventoryList
traverse = context.getPortalObject().restrictedTraverse
getObject = context.getPortalObject().portal_catalog.getObject
Base_translateString = portal.Base_translateString
selected_gap = gap_root

inventory_movement_type_list = portal.getPortalInventoryMovementTypeList()
# Balance Movement Type list is all movements that are both inventory movement
# and accounting movement
balance_movement_type_list = [ t for t in
                               portal.getPortalAccountingMovementTypeList()
                               if t in inventory_movement_type_list ]

accounting_movement_type_list = [ t for t in
                                  portal.getPortalAccountingMovementTypeList()
                                  if t not in balance_movement_type_list ]

inventory_params = dict(section_uid=section_uid,
                        simulation_state=simulation_state,
                        precision=precision,
                        group_by_resource=0)

if group_analytic:
  inventory_params['group_by'] = group_analytic
  group_analytic = tuple(group_analytic)

if portal_type and portal_type != portal.getPortalAccountingTransactionTypeList():
  inventory_params['parent_portal_type'] = portal_type
if function:
  if function == 'None':
    inventory_params['function_uid'] = Query(function_uid=None)
  else:
    function_value = portal.restrictedTraverse(function, None)
    if function_value is not None and function_value.getPortalType() != 'Category':
      inventory_params['function_uid'] = function_value.getUid()
    else:
      inventory_params['function_category'] = function
if funding:
  if funding == 'None':
    inventory_params['funding_uid'] = Query(funding_uid=None)
  else:
    funding_value = portal.restrictedTraverse(funding, None)
    if funding_value is not None and funding_value.getPortalType() != 'Category':
      inventory_params['funding_uid'] = funding_value.getUid()
    else:
      inventory_params['funding_category'] = funding
if project:
  if project == 'None':
    inventory_params['project_uid'] = Query(project_uid=None)
  else:
    inventory_params['project'] = project
if mirror_section_category:
  inventory_params['mirror_section_category'] = mirror_section_category

if node_uid:
  inventory_params['node_uid'] = node_uid

MARKER = Object()

# a dictionary (node_relative_url, mirror_section_uid, payment_uid + analytic)
#                        -> dict(debit=, credit=)
line_per_account = {}
# a dictionnary node_relative_url -> boolean "do we have transactions for this
# account ?"
account_used = {}

account_type = portal.portal_categories.account_type
balance_sheet_account_type_list = [c[0] for c in 
 account_type.asset.getCategoryChildItemList(base=1, is_self_excluded=False, display_none_category=False ) + \
 account_type.equity.getCategoryChildItemList(base=1, is_self_excluded=False, display_none_category=False) + \
 account_type.liability.getCategoryChildItemList(base=1, is_self_excluded=False, display_none_category=False) ]

profit_and_loss_account_type = [
                  'account_type/expense',
                  'account_type/income',]

account_type_to_group_by_payment = [ 'account_type/asset/cash/bank' ]

account_type_payable_receivable = [
                  'account_type/asset/receivable',
                  'account_type/liability/payable', ]


# For initial balance of third party accounts, we want the same bottom line figure for initial
# debit and initial debit wether or not we expand accounts.
#
# For example if we have this balance when enabling the detailed breakdown
# by third party for payable & recievable accounts:
#
# Account | Third Party | Initial Debit Balance | Initial Credit Balance |
# --------+-------------+-----------------------+------------------------|
#   A1    | P1          |                   100 |                        |
#   A1    | P2          |                       |                     30 |
#
# When the breakdown is disabled, we still want to have:
#
# Account | Initial Debit Balance | Initial Credit Balance |
# --------+-----------------------+------------------------|
#   A1    |                   100 |                     30 |
#
# and not an initial debit balance of 70.
# This behaviour applies to initial balances, not movements in the period.
#
# Inventory API does not provide such feature of a getInventory(omit_input/output=True) that
# does a sum of getInventoryList(omit_input/output=True, group_by_node=True), so we sum this up
# in python, which becomes heavy when there are a lot of third parties (even if we do not
# enable the break down).
# If user does not enable detailed columns, then there is only one column for initial balance,
# so the complexity described above does not apply.
if expand_accounts:
  account_type_to_group_by_mirror_section = account_type_payable_receivable
  account_type_to_group_by_mirror_section_previous_period = account_type_payable_receivable
else:
  account_type_to_group_by_mirror_section = []
  account_type_to_group_by_mirror_section_previous_period = []
  if show_detailed_balance_columns:
    account_type_to_group_by_mirror_section_previous_period = account_type_payable_receivable


account_type_to_group_by_node = [at for at in balance_sheet_account_type_list
  if at not in account_type_to_group_by_payment
  and at not in account_type_to_group_by_mirror_section]

account_type_to_group_by_node_previous_period = [at for at in account_type_to_group_by_node
  if at not in account_type_to_group_by_mirror_section_previous_period]


total_debit = 0
total_credit = 0
total_initial_debit_balance = 0
total_initial_credit_balance = 0
total_final_balance_if_debit = 0
total_final_balance_if_credit = 0

def getKey(brain, mirror_section=MARKER, payment=MARKER, all_empty=False):
  key = (brain['node_relative_url'],
         mirror_section,
         payment)
  for analytic in group_analytic:
    if all_empty:
      key += (MARKER, )
    elif hasattr(brain, analytic):
      key += (getattr(brain, analytic), )
    else:
      key += (brain.getObject().getProperty(analytic.replace('strict_', '', 1)), )
  return key

analytic_title_dict = {None: '', }
def getAnalyticTitleFromUid(uid):
  if uid is MARKER:
    return ''
  try:
    return analytic_title_dict[uid]
  except KeyError:
    node = getObject(uid)
    title = node.getTranslatedTitle()
    reference = node.getReference()
    if reference:
      title = '%s - %s' % (reference, title)
    return analytic_title_dict.setdefault(uid, title)

section_price_currency_dict = {None: ''}
def getSectionPriceCurrencyFromSectionUid(uid):
  if uid is MARKER:
    return ''
  try:
    return section_price_currency_dict[uid]
  except KeyError:
    section = getObject(uid)
    price_currency = ''
    if section is not None:
      price_currency = section.getProperty('price_currency_reference')
    return section_price_currency_dict.setdefault(uid, price_currency)

# standards accounts {{{
for node in getInventoryList(
                node_category_strict_membership=account_type_to_group_by_node,
                group_by_node=1,
                omit_asset_decrease=1,
                from_date=from_date,
                at_date=at_date,
                portal_type=accounting_movement_type_list,
                **inventory_params):
  account_used[node['node_relative_url']] = 1
  account_props = line_per_account.setdefault(getKey(node), dict(debit=0, credit=0))
  total_price = node['total_price'] or 0
  account_props['debit'] = total_price
  total_debit += round(total_price, precision)

for node in getInventoryList(
                node_category_strict_membership=account_type_to_group_by_node,
                group_by_node=1,
                omit_asset_increase=1,
                from_date=from_date,
                at_date=at_date,
                portal_type=accounting_movement_type_list,
                **inventory_params):
  account_used[node['node_relative_url']] = 1
  account_props = line_per_account.setdefault(getKey(node), dict(debit=0, credit=0))
  total_price = node['total_price'] or 0
  account_props['credit'] = -total_price
  total_credit -= round(total_price, precision)
# }}}

### profit & loss accounts {{{
for node in getInventoryList(
                node_category=profit_and_loss_account_type,
                from_date=max(period_start_date, from_date),
                group_by_node=1,
                omit_asset_decrease=1,
                at_date=at_date,
                portal_type=accounting_movement_type_list,
                **inventory_params):
  account_used[node['node_relative_url']] = 1
  account_props = line_per_account.setdefault(getKey(node), dict(debit=0, credit=0))
  total_price = node['total_price'] or 0
  account_props['debit'] = total_price
  total_debit += round(total_price, precision)

for node in getInventoryList(
                node_category=profit_and_loss_account_type,
                from_date=max(period_start_date, from_date),
                group_by_node=1,
                omit_asset_increase=1,
                at_date=at_date,
                portal_type=accounting_movement_type_list,
                **inventory_params):
  account_used[node['node_relative_url']] = 1
  account_props = line_per_account.setdefault(getKey(node), dict(debit=0, credit=0))
  total_price = node['total_price'] or 0
  account_props['credit'] = -total_price
  total_credit -= round(total_price, precision)
# }}}

# payable / receivable accounts {{{
if account_type_to_group_by_mirror_section:
  for node in getInventoryList(
                  node_category_strict_membership=
                          account_type_to_group_by_mirror_section,
                  group_by_mirror_section=1,
                  group_by_node=1,
                  omit_asset_decrease=1,
                  from_date=from_date,
                  at_date=at_date,
                  portal_type=accounting_movement_type_list,
                  **inventory_params):
    account_used[node['node_relative_url']] = 1
    account_props = line_per_account.setdefault(
          getKey(node, mirror_section=node['mirror_section_uid']),
          dict(debit=0, credit=0))
    total_price = node['total_price'] or 0
    account_props['debit'] = total_price
    total_debit += round(total_price, precision)

  for node in getInventoryList(
                  node_category_strict_membership=
                          account_type_to_group_by_mirror_section,
                  group_by_mirror_section=1,
                  group_by_node=1,
                  omit_asset_increase=1,
                  from_date=from_date,
                  at_date=at_date,
                  portal_type=accounting_movement_type_list,
                  **inventory_params):
    account_used[node['node_relative_url']] = 1
    account_props = line_per_account.setdefault(
          getKey(node, mirror_section=node['mirror_section_uid']),
          dict(debit=0, credit=0))
    total_price = node['total_price'] or 0
    account_props['credit'] = - total_price
    total_credit -= round(total_price, precision)
# }}}

# bank accounts {{{
if account_type_to_group_by_payment:
  for node in getInventoryList(
                  node_category_strict_membership=
                          account_type_to_group_by_payment,
                  group_by_payment=1,
                  group_by_node=1,
                  omit_asset_decrease=1,
                  from_date=from_date,
                  at_date=at_date,
                  portal_type=accounting_movement_type_list,
                  **inventory_params):
    account_used[node['node_relative_url']] = 1
    account_props = line_per_account.setdefault(
          getKey(node, payment=node['payment_uid']),
          dict(debit=0, credit=0))
    total_price = node['total_price'] or 0
    account_props['debit'] = total_price
    total_debit += round(total_price, precision)

  for node in getInventoryList(
                  node_category_strict_membership=
                          account_type_to_group_by_payment,
                  group_by_payment=1,
                  group_by_node=1,
                  omit_asset_increase=1,
                  from_date=from_date,
                  at_date=at_date,
                  portal_type=accounting_movement_type_list,
                  **inventory_params):
    account_used[node['node_relative_url']] = 1
    account_props = line_per_account.setdefault(
          getKey(node, payment=node['payment_uid']),
          dict(debit=0, credit=0))
    total_price = node['total_price'] or 0
    account_props['credit'] = - total_price
    total_credit -= round(total_price, precision)
  # }}}


node_title_and_id_cache = {}
def getNodeTitleAndId(node_relative_url):
  try:
    return node_title_and_id_cache[node_relative_url]
  except KeyError:
    node = traverse(node_relative_url)
    return node_title_and_id_cache.setdefault(node_relative_url,
                  ( node.getUid(),
                    node.getTranslatedTitle(),
                    node.Account_getGapId(gap_root=selected_gap),
                    node.getProperty('string_index'),
                    node))

# include all accounts, even those not selected before (no movements in the
# period)
for node in LazyFilter(context.account_module.contentValues(), skip=''):
  if node.getRelativeUrl() not in account_used:
    line_per_account.setdefault(
          getKey(dict(node_relative_url=node.getRelativeUrl()), all_empty=True),
          dict(debit=0, credit=0))

initial_balance_date = (from_date - 1).latestTime()

# Initial Balance

# standards accounts {{{
# balance at period start date
for node in getInventoryList(
                node_category_strict_membership=
                   account_type_to_group_by_node_previous_period,
                group_by_node=1,
                to_date=period_start_date,
                portal_type=accounting_movement_type_list +
                              balance_movement_type_list,
                **inventory_params):
  account_props = line_per_account.setdefault(getKey(node), dict(debit=0, credit=0))
  total_price = node['total_price'] or 0
  account_props['initial_balance'] = account_props.get(
              'initial_balance', 0) + total_price
  account_props['initial_debit_balance'] = account_props.get(
              'initial_debit_balance', 0) + max(total_price, 0)
  account_props['initial_credit_balance'] = account_props.get(
              'initial_credit_balance', 0) + max(- total_price, 0)

found_balance = False
# Balance Transaction
for node in getInventoryList(
                node_category_strict_membership=
                   account_type_to_group_by_node_previous_period,
                group_by_node=1,
                from_date=from_date,
                at_date=from_date + 1,
                portal_type=balance_movement_type_list,
                **inventory_params):
  account_props = line_per_account.setdefault(getKey(node), dict(debit=0, credit=0))
  total_price = node['total_price'] or 0
  account_props['initial_balance'] = account_props.get(
              'initial_balance', 0) + total_price
  account_props['initial_debit_balance'] = account_props.get(
              'initial_debit_balance', 0) + max(total_price, 0)
  account_props['initial_credit_balance'] = account_props.get(
              'initial_credit_balance', 0) + max(- total_price, 0)
  found_balance = True

period_movement_type_list = accounting_movement_type_list
if not found_balance:
  period_movement_type_list = accounting_movement_type_list +\
      balance_movement_type_list

for node in getInventoryList(
                node_category_strict_membership=
                          account_type_to_group_by_node,
                group_by_node=1,
                omit_asset_decrease=1,
                from_date=period_start_date,
                to_date=from_date,
                portal_type=period_movement_type_list,
                **inventory_params):
  account_props = line_per_account.setdefault(getKey(node), dict(debit=0, credit=0))
  total_price = node['total_price'] or 0
  account_props['initial_debit_balance'] = account_props.get(
                    'initial_debit_balance', 0) + total_price

for node in getInventoryList(
                node_category_strict_membership=
                          account_type_to_group_by_node,
                group_by_node=1,
                omit_asset_increase=1,
                from_date=period_start_date,
                to_date=from_date,
                portal_type=period_movement_type_list,
                **inventory_params):
  account_props = line_per_account.setdefault(getKey(node), dict(debit=0, credit=0))
  total_price = node['total_price'] or 0
  account_props['initial_credit_balance'] = account_props.get(
                    'initial_credit_balance', 0) - total_price
# }}}

### profit & loss accounts {{{
for node in getInventoryList(
                node_category=profit_and_loss_account_type,
                omit_asset_decrease=1,
                from_date=min(period_start_date,
                              initial_balance_date),
                at_date=initial_balance_date,
                group_by_node=1,
                portal_type=accounting_movement_type_list,
                **inventory_params):
  account_props = line_per_account.setdefault(getKey(node), dict(debit=0, credit=0))
  total_price = node['total_price'] or 0
  account_props['initial_debit_balance'] = account_props.get(
                    'initial_debit_balance', 0) + total_price

for node in getInventoryList(
                node_category=profit_and_loss_account_type,
                omit_asset_increase=1,
                from_date=min(period_start_date,
                              initial_balance_date),
                at_date=initial_balance_date,
                group_by_node=1,
                portal_type=accounting_movement_type_list,
                **inventory_params):
  account_props = line_per_account.setdefault(getKey(node), dict(debit=0, credit=0))
  total_price = node['total_price'] or 0
  account_props['initial_credit_balance'] = account_props.get(
                    'initial_credit_balance', 0) - total_price
# }}}

# payable / receivable accounts {{{
# initial balance
if account_type_to_group_by_mirror_section_previous_period:
  for node in getInventoryList(
                  node_category_strict_membership=account_type_to_group_by_mirror_section_previous_period,
                  group_by_mirror_section=1,
                  group_by_node=1,
                  to_date=period_start_date,
                  portal_type=accounting_movement_type_list +
                                balance_movement_type_list,
                  **inventory_params):
    mirror_section_key = MARKER
    if expand_accounts:
      mirror_section_key = node['mirror_section_uid']

    account_props = line_per_account.setdefault(
                      getKey(node, mirror_section=mirror_section_key),
                             dict(debit=0, credit=0))
    total_price = node['total_price'] or 0
    account_props['initial_debit_balance'] = account_props.get(
                    'initial_debit_balance', 0) + max(total_price, 0)
    account_props['initial_credit_balance'] = account_props.get(
                   'initial_credit_balance', 0) + max(-total_price, 0)

found_balance=False
# Balance Transactions
if account_type_to_group_by_mirror_section_previous_period:
  for node in getInventoryList(
                  node_category_strict_membership=account_type_to_group_by_mirror_section_previous_period,
                  group_by_mirror_section=1,
                  group_by_node=1,
                  from_date=from_date,
                  at_date=from_date + 1,
                  portal_type=balance_movement_type_list,
                  **inventory_params):
    mirror_section_key = MARKER
    if expand_accounts:
      mirror_section_key = node['mirror_section_uid']
    account_props = line_per_account.setdefault(
            getKey(node, mirror_section=mirror_section_key),
                   dict(debit=0, credit=0))
    total_price = node['total_price'] or 0
    account_props['initial_debit_balance'] = account_props.get(
                'initial_debit_balance', 0) + max(total_price, 0)
    account_props['initial_credit_balance'] = account_props.get(
                'initial_credit_balance', 0) + max(- total_price, 0)
    found_balance=True


period_movement_type_list = accounting_movement_type_list
if not found_balance:
  period_movement_type_list = accounting_movement_type_list +\
      balance_movement_type_list


if expand_accounts:
  for node in getInventoryList(
                  node_category_strict_membership=
                          account_type_to_group_by_mirror_section,
                  group_by_mirror_section=1,
                  group_by_node=1,
                  omit_asset_decrease=1,
                  from_date=period_start_date,
                  to_date=from_date,
                  portal_type=period_movement_type_list,
                  **inventory_params):
    account_props = line_per_account.setdefault(
          getKey(node, mirror_section=node['mirror_section_uid']),
                 dict(debit=0, credit=0))
    total_price = node['total_price'] or 0
    account_props['initial_debit_balance'] = account_props.get(
                      'initial_debit_balance', 0) + total_price

  for node in getInventoryList(
                  node_category_strict_membership=
                          account_type_to_group_by_mirror_section,
                  group_by_mirror_section=1,
                  group_by_node=1,
                  omit_asset_increase=1,
                  from_date=period_start_date,
                  to_date=from_date,
                  portal_type=period_movement_type_list,
                  **inventory_params):
    account_props = line_per_account.setdefault(
          getKey(node, mirror_section=node['mirror_section_uid']),
                 dict(debit=0, credit=0))
    total_price = node['total_price'] or 0
    account_props['initial_credit_balance'] = account_props.get(
                      'initial_credit_balance', 0) - total_price
# }}}

# bank accounts {{{
if account_type_to_group_by_payment:
  # Initial balance
  for node in getInventoryList(
                  node_category_strict_membership=
                          account_type_to_group_by_payment,
                  group_by_payment=1,
                  group_by_node=1,
                  to_date=period_start_date,
                  portal_type=accounting_movement_type_list +
                                balance_movement_type_list,
                  **inventory_params):
    account_props = line_per_account.setdefault(
          getKey(node, payment=node['payment_uid']),
                 dict(debit=0, credit=0))
    total_price = node['total_price'] or 0
    account_props['initial_debit_balance'] = account_props.get(
                    'initial_debit_balance', 0) + max(total_price, 0)
    account_props['initial_credit_balance'] = account_props.get(
                   'initial_credit_balance', 0) + max(- total_price, 0)

  found_balance = False
  # Balance Transaction
  for node in getInventoryList(
                  node_category_strict_membership=
                          account_type_to_group_by_payment,
                  group_by_payment=1,
                  group_by_node=1,
                  from_date=from_date,
                  at_date=from_date + 1,
                  portal_type=balance_movement_type_list,
                  **inventory_params):
    account_used[node['node_relative_url']] = 1
    account_props = line_per_account.setdefault(
          getKey(node, payment=node['payment_uid']),
                 dict(debit=0, credit=0))
    total_price = node['total_price'] or 0
    total_price += account_props.get('initial_debit_balance', 0)
    total_price -= account_props.get('initial_credit_balance', 0)
    account_props['initial_debit_balance'] = max(total_price, 0)
    account_props['initial_credit_balance'] = max(- total_price, 0)
    found_balance = True

  period_movement_type_list = accounting_movement_type_list
  if not found_balance:
    period_movement_type_list = accounting_movement_type_list +\
        balance_movement_type_list
  for node in getInventoryList(
                  node_category_strict_membership=
                          account_type_to_group_by_payment,
                  group_by_payment=1,
                  group_by_node=1,
                  omit_asset_decrease=1,
                  from_date=period_start_date,
                  to_date=from_date,
                  portal_type=period_movement_type_list,
                  **inventory_params):
    account_used[node['node_relative_url']] = 1
    account_props = line_per_account.setdefault(
          getKey(node, payment=node['payment_uid']),
                 dict(debit=0, credit=0))
    total_price = node['total_price'] or 0
    account_props['initial_debit_balance'] = account_props.get(
                      'initial_debit_balance', 0) + total_price

  for node in getInventoryList(
                  node_category_strict_membership=
                          account_type_to_group_by_payment,
                  group_by_payment=1,
                  group_by_node=1,
                  omit_asset_increase=1,
                  from_date=period_start_date,
                  to_date=from_date,
                  portal_type=period_movement_type_list,
                  **inventory_params):
    account_used[node['node_relative_url']] = 1
    account_props = line_per_account.setdefault(
          getKey(node, payment=node['payment_uid']),
                 dict(debit=0, credit=0))
    total_price = node['total_price'] or 0
    account_props['initial_credit_balance'] = account_props.get(
                      'initial_credit_balance', 0) - total_price
  # }}}

line_list = []
for key, data in line_per_account.items():
  node_relative_url = key[0]
  mirror_section_uid = key[1]
  payment_uid = key[2]
  analytic_key_list = key[3:]

  mirror_section_title = None
  if expand_accounts and mirror_section_uid is not MARKER:
    mirror_section_title = getObject(mirror_section_uid).getTitle()

  node_uid, node_title, node_id, node_string_index, node =\
          getNodeTitleAndId(node_relative_url)

  if selected_gap and not node.isMemberOf(selected_gap):
    continue

  if payment_uid is not MARKER:
    if payment_uid is None:
      node_title = '%s (%s)' % ( node_title, Base_translateString('None'))
    else:
      payment = getObject(payment_uid)
      node_title = "%s (%s)" % ( node_title, payment.getTitle() )

  if not node_string_index:
    node_string_index = '%-10s' % node_id

  initial_debit_balance = data.get('initial_debit_balance', 0)
  initial_credit_balance = data.get('initial_credit_balance', 0)

  total_initial_debit_balance += round(initial_debit_balance, precision)
  total_initial_credit_balance += round(initial_credit_balance, precision)
  final_debit_balance = round(initial_debit_balance + data['debit'],
                              precision)
  final_credit_balance = round(initial_credit_balance + data['credit'],
                               precision)
  closing_balance = final_debit_balance - final_credit_balance
  total_final_balance_if_debit += round(max(closing_balance, 0), precision)
  total_final_balance_if_credit += round(max(-closing_balance, 0) or 0, precision)

  line = Object(uid='new_',
                node_id=node_id,
                node_title=node_title,
                mirror_section_title=mirror_section_title,
                node_relative_url=node_relative_url,
                initial_balance=initial_debit_balance - initial_credit_balance,
                initial_debit_balance=initial_debit_balance,
                initial_credit_balance=initial_credit_balance,
                debit=data['debit'],
                credit=data['credit'],
                final_balance=final_debit_balance - final_credit_balance,
                final_debit_balance=final_debit_balance,
                final_credit_balance=final_credit_balance,
                final_balance_if_debit=max(closing_balance, 0),
                final_balance_if_credit=max(-closing_balance, 0) or 0,)

  sort_key = (node_string_index, node_title, mirror_section_title)
  analytic_dict = {}
  for analytic, uid in zip(group_analytic, analytic_key_list):
    title = getAnalyticTitleFromUid(uid)
    analytic_dict[analytic] = title
    if analytic == 'section_uid':
      analytic_dict['Movement_getSectionPriceCurrency'] = getSectionPriceCurrencyFromSectionUid(uid)
      # We sort on section title first
      sort_key = (title, ) + sort_key
    sort_key += (title, )
    
  analytic_dict['sort_key'] = sort_key
  line.update(analytic_dict)
  line_list.append(line)
  

if not show_empty_accounts:
  line_list = [ line for line in line_list
                if line['debit'] or
                   line['credit'] or
                   line['initial_credit_balance'] or
                   line['initial_debit_balance'] ]

line_list.sort(key=lambda obj:obj['sort_key'])

# cache values for stat
request.set('TrialBalance.total_initial_debit_balance',
            total_initial_debit_balance)
request.set('TrialBalance.total_initial_credit_balance',
            total_initial_credit_balance)
request.set('TrialBalance.debit', total_debit)
request.set('TrialBalance.credit', total_credit)
request.set('TrialBalance.final_balance_if_debit', total_final_balance_if_debit)
request.set('TrialBalance.final_balance_if_credit', total_final_balance_if_credit)

if not per_account_class_summary:
  return line_list

current_gap = selected_gap or \
                 portal.portal_preferences.getPreferredAccountingTransactionGap() or ''
if current_gap.startswith('gap/'):
  current_gap = current_gap[4:]
def getAccountClass(account_relative_url):
  account = traverse(account_relative_url)
  for gap in account.getGapList():
    if gap.startswith(current_gap):
      gap_part_list = gap.split('/')
      # country / accounting principle / ${class}
      if len(gap_part_list) > 2:
        return gap_part_list[2]
  return None # this account has no class on the current GAP  

new_line_list = []
account_per_class = {}
for brain in line_list:
  account_per_class.setdefault(
      getAccountClass(brain.node_relative_url), []).append(brain)

account_class_list = account_per_class.keys()
account_class_list.sort()

add_line = new_line_list.append
for account_class in account_class_list:
  initial_debit_balance = 0
  debit = 0
  final_debit_balance = 0
  initial_credit_balance = 0
  credit = 0
  final_credit_balance = 0
  final_balance_if_debit = 0
  final_balance_if_credit = 0

  for account in account_per_class[account_class]:
    initial_debit_balance += account.initial_debit_balance
    debit += account.debit
    final_debit_balance += account.final_debit_balance
    initial_credit_balance += account.initial_credit_balance
    credit += account.credit
    final_credit_balance += account.final_credit_balance
    final_balance_if_debit += account.final_balance_if_debit
    final_balance_if_credit += account.final_balance_if_credit
    add_line(account)

  # summary
  add_line(Object(node_title=Base_translateString('Total for class ${account_class}',
                   mapping=dict(account_class=account_class or '???')),
          initial_balance=round(initial_debit_balance - initial_credit_balance, precision),
          initial_debit_balance=round(initial_debit_balance, precision),
          debit=round(debit, precision),
          final_debit_balance=round(final_debit_balance, precision),
          initial_credit_balance=round(initial_credit_balance, precision),
          credit=round(credit, precision),
          final_credit_balance=round(final_credit_balance, precision),
          final_balance_if_debit=round(final_balance_if_debit, precision),
          final_balance_if_credit=round(final_balance_if_credit, precision),
          final_balance=round(final_debit_balance - final_credit_balance, precision),))

  add_line(Object(node_title=' '))

return new_line_list
# vim: foldmethod=marker
