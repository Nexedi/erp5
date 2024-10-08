from Products.ZSQLCatalog.SQLCatalog import SimpleQuery
from Products.PythonScripts.standard import Object
from ZTUtils import LazyFilter
import six

portal = context.getPortalObject()
portal_categories = portal.portal_categories
request = portal.REQUEST
getInventoryList_ = portal.portal_simulation.getInventoryList
traverse = portal.restrictedTraverse
portal_catalog = portal.portal_catalog
Base_translateString = portal.Base_translateString
selected_gap = gap_root
traverseCategory = portal.portal_categories.restrictedTraverse
def getAccountUidListByCategory(category, strict_membership):
  """
  Transform node_category* into node_uid list.
  """
  if not category:
    return []
  kw = {
    ('strict_' if strict_membership else '') + 'account_type_uid': [
      traverseCategory(x).getUid() for x in category
    ],
  }
  if node_uid:
    kw['uid'] = node_uid
  return [x.uid for x in portal_catalog(portal_type='Account', **kw)]

inventory_movement_type_list = portal.getPortalInventoryMovementTypeList()
# Balance Movement Type list is all movements that are both inventory movement
# and accounting movement
balance_movement_type_list = [
  t for t in portal.getPortalAccountingMovementTypeList()
  if t in inventory_movement_type_list
]
accounting_movement_type_list = [
  t for t in portal.getPortalAccountingMovementTypeList()
  if t not in balance_movement_type_list
]

src_list = []
def getInventoryList(node_uid=None, **kw):
  if not node_uid and node_uid is not None:
    return []
  for key, value in six.iteritems(inventory_params):
    assert key not in kw, key
    kw[key] = value
  result = getInventoryList_(
    section_uid=section_uid,
    simulation_state=simulation_state,
    precision=precision,
    group_by_resource=0,
    group_by_node=1,
    node_uid=node_uid,
    src__=src__,
    **kw
  )
  if src__:
    src_list.append(result)
    return []
  return result
inventory_params = {}
if group_analytic:
  inventory_params['group_by'] = group_analytic
  group_analytic = tuple(group_analytic)
if portal_type and set(portal_type) != set(portal.getPortalAccountingTransactionTypeList()):
  inventory_params['parent_portal_type'] = portal_type
if function:
  if function == 'None':
    inventory_params['function_uid'] = SimpleQuery(function_uid=None)
  else:
    function_value = portal.restrictedTraverse(function, None)
    if function_value is not None and function_value.getPortalType() != 'Category':
      inventory_params['function_uid'] = function_value.getUid()
    else:
      inventory_params['function_category'] = function
if funding:
  if funding == 'None':
    inventory_params['funding_uid'] = SimpleQuery(funding_uid=None)
  else:
    funding_value = portal.restrictedTraverse(funding, None)
    if funding_value is not None and funding_value.getPortalType() != 'Category':
      inventory_params['funding_uid'] = funding_value.getUid()
    else:
      inventory_params['funding_category'] = funding
if project:
  if project == 'None':
    inventory_params['project_uid'] = SimpleQuery(project_uid=None)
  else:
    inventory_params['project'] = project
if mirror_section_category:
  inventory_params['mirror_section_category'] = mirror_section_category

if ledger:
  if ledger == 'None':
    inventory_params['ledger_uid'] = SimpleQuery(ledger_uid=None)
  else:
    if not isinstance(ledger, list):
      # Allows the generation of reports on different ledgers as the same time
      ledger = [ledger]
    ledger_value_list = [portal_categories.restrictedTraverse(ledger_category, None)
                         for ledger_category in ledger]
    for ledger_value in ledger_value_list:
      inventory_params.setdefault('ledger_uid', []).append(ledger_value.getUid())

# a dictionary (node_relative_url, mirror_section_uid, payment_uid + analytic)
#                        -> {'debit'=, 'credit'=}
line_per_account = {}
account_used = set()
def markNodeUsed(node):
  account_used.add(node['node_relative_url'])
def getTotalPrice(node):
  return node['total_price'] or 0

account_type = portal.portal_categories.account_type
balance_sheet_account_type_list = [c[0] for c in
  account_type.asset.getCategoryChildItemList(base=1, is_self_excluded=False, display_none_category=False) +
  account_type.equity.getCategoryChildItemList(base=1, is_self_excluded=False, display_none_category=False) +
  account_type.liability.getCategoryChildItemList(base=1, is_self_excluded=False, display_none_category=False)
]

profit_and_loss_account_uid_list = getAccountUidListByCategory(
  [
    'account_type/expense',
    'account_type/income',
  ],
  strict_membership=0,
)

account_type_to_group_by_payment = [
  'account_type/asset/cash/bank'
]
node_uid_of_strict_account_type_to_group_by_payment = getAccountUidListByCategory(
  account_type_to_group_by_payment,
  strict_membership=1,
)

account_type_payable_receivable = [
  'account_type/asset/receivable',
  'account_type/liability/payable',
]


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
  if show_detailed_balance_columns:
    account_type_to_group_by_mirror_section_previous_period = account_type_payable_receivable
  else:
    account_type_to_group_by_mirror_section_previous_period = []
node_uid_of_strict_account_type_to_group_by_mirror_section = getAccountUidListByCategory(
  category=account_type_to_group_by_mirror_section,
  strict_membership=1,
)

account_type_to_group_by_node = [
  x for x in balance_sheet_account_type_list
  if x not in account_type_to_group_by_payment and x not in account_type_to_group_by_mirror_section
]
node_uid_of_strict_account_type_to_group_by_node = getAccountUidListByCategory(
  category=account_type_to_group_by_node,
  strict_membership=1,
)

total_debit = 0
total_credit = 0
total_initial_debit_balance = 0
total_initial_credit_balance = 0
total_final_balance_if_debit = 0
total_final_balance_if_credit = 0

MARKER = Object()
def getAccountProps(brain, mirror_section=MARKER, payment=MARKER, all_empty=False):
  key = (brain['node_relative_url'], mirror_section, payment)
  for analytic in group_analytic:
    if all_empty:
      key += (MARKER, )
    elif hasattr(brain, analytic):
      key += (getattr(brain, analytic), )
    else:
      key += (brain.getObject().getProperty(analytic.replace('strict_', '', 1)), )
  try:
    value = line_per_account[key]
  except KeyError:
    line_per_account[key] = value = {'debit': 0, 'credit': 0}
  return value

def addAccountProps(entry_list, *args, **kw):
  account_props = getAccountProps(*args, **kw)
  for key, value in entry_list:
    account_props[key] = account_props.get(key, 0) + value

# standards accounts {{{
local_inventory_params = {
  'node_uid': node_uid_of_strict_account_type_to_group_by_node,
  'from_date': from_date,
  'at_date': at_date,
  'portal_type': accounting_movement_type_list,
}
for node in getInventoryList(omit_asset_decrease=1, **local_inventory_params):
  markNodeUsed(node)
  total_price = getTotalPrice(node)
  getAccountProps(node)['debit'] = total_price
  total_debit += round(total_price, precision)
for node in getInventoryList(omit_asset_increase=1, **local_inventory_params):
  markNodeUsed(node)
  total_price = getTotalPrice(node)
  getAccountProps(node)['credit'] = -total_price
  total_credit -= round(total_price, precision)
# }}}

### profit & loss accounts {{{
local_inventory_params = {
  'node_uid': profit_and_loss_account_uid_list,
  'from_date': max(period_start_date, from_date),
  'at_date': at_date,
  'portal_type': accounting_movement_type_list,
}
for node in getInventoryList(omit_asset_decrease=1, **local_inventory_params):
  markNodeUsed(node)
  total_price = getTotalPrice(node)
  getAccountProps(node)['debit'] = total_price
  total_debit += round(total_price, precision)
for node in getInventoryList(omit_asset_increase=1, **local_inventory_params):
  markNodeUsed(node)
  total_price = getTotalPrice(node)
  getAccountProps(node)['credit'] = -total_price
  total_credit -= round(total_price, precision)
# }}}

# payable / receivable accounts {{{
if node_uid_of_strict_account_type_to_group_by_mirror_section:
  if src__:
    src_list.append('-- payable / receivable accounts')
  local_inventory_params = {
    'node_uid': node_uid_of_strict_account_type_to_group_by_mirror_section,
    'group_by_mirror_section': 1,
    'from_date': from_date,
    'at_date': at_date,
    'portal_type': accounting_movement_type_list,
  }
  for node in getInventoryList(omit_asset_decrease=1, **local_inventory_params):
    markNodeUsed(node)
    total_price = getTotalPrice(node)
    getAccountProps(node, mirror_section=node['mirror_section_uid'])['debit'] = total_price
    total_debit += round(total_price, precision)
  for node in getInventoryList(omit_asset_increase=1, **local_inventory_params):
    markNodeUsed(node)
    total_price = getTotalPrice(node)
    getAccountProps(node, mirror_section=node['mirror_section_uid'])['credit'] = -total_price
    total_credit -= round(total_price, precision)
# }}}

# bank accounts {{{
if node_uid_of_strict_account_type_to_group_by_payment:
  if src__:
    src_list.append('-- bank accounts')
  local_inventory_params = {
    'node_uid': node_uid_of_strict_account_type_to_group_by_payment,
    'group_by_payment': 1,
    'from_date': from_date,
    'at_date': at_date,
    'portal_type': accounting_movement_type_list,
  }
  for node in getInventoryList(omit_asset_decrease=1, **local_inventory_params):
    markNodeUsed(node)
    total_price = getTotalPrice(node)
    getAccountProps(node, payment=node['payment_uid'])['debit'] = total_price
    total_debit += round(total_price, precision)
  for node in getInventoryList(omit_asset_increase=1, **local_inventory_params):
    markNodeUsed(node)
    total_price = getTotalPrice(node)
    getAccountProps(node, payment=node['payment_uid'])['credit'] = - total_price
    total_credit -= round(total_price, precision)
# }}}

# include all accounts, even those not selected before (no movements in the
# period)
for node in LazyFilter(portal.account_module.contentValues(), skip=''):
  if node.getRelativeUrl() not in account_used:
    getAccountProps(
      {
        'node_relative_url': node.getRelativeUrl(),
      },
      all_empty=True,
    )

initial_balance_date = (from_date - 1).latestTime()

# Initial Balance

# standards accounts {{{
# balance at period start date
local_inventory_params = {
  'node_uid': getAccountUidListByCategory(
    [
      x for x in account_type_to_group_by_node
      if x not in account_type_to_group_by_mirror_section_previous_period
    ],
    strict_membership=1,
  ),
}
for node in getInventoryList(
      to_date=period_start_date,
      portal_type=accounting_movement_type_list + balance_movement_type_list,
      **local_inventory_params
    ):
  total_price = getTotalPrice(node)
  addAccountProps(
    (
      ('initial_balance', total_price),
      ('initial_debit_balance', max(total_price, 0)),
      ('initial_credit_balance', max(-total_price, 0)),
    ),
    node,
  )
found_balance = False
# Balance Transaction
for node in getInventoryList(
      from_date=from_date,
      at_date=from_date + 1,
      portal_type=balance_movement_type_list,
      **local_inventory_params
    ):
  total_price = getTotalPrice(node)
  addAccountProps(
    (
      ('initial_balance', total_price),
      ('initial_debit_balance', max(total_price, 0)),
      ('initial_credit_balance', max(-total_price, 0)),
    ),
    node,
  )
  found_balance = True
period_movement_type_list = accounting_movement_type_list
if not found_balance:
  period_movement_type_list += balance_movement_type_list
local_inventory_params = {
  'node_uid': node_uid_of_strict_account_type_to_group_by_node,
  'from_date': period_start_date,
  'to_date': from_date,
  'portal_type': period_movement_type_list,
}
for node in getInventoryList(omit_asset_decrease=1, **local_inventory_params):
  addAccountProps(
    (
      ('initial_debit_balance', getTotalPrice(node)),
    ),
    node,
  )
for node in getInventoryList(omit_asset_increase=1, **local_inventory_params):
  addAccountProps(
    (
      ('initial_credit_balance', -(getTotalPrice(node))),
    ),
    node,
  )
# }}}

### profit & loss accounts {{{
local_inventory_params = {
  'node_uid': profit_and_loss_account_uid_list,
  'from_date': min(period_start_date, initial_balance_date),
  'at_date': initial_balance_date,
  'portal_type': accounting_movement_type_list,
}
for node in getInventoryList(omit_asset_decrease=1, **local_inventory_params):
  addAccountProps(
    (
      ('initial_debit_balance', getTotalPrice(node)),
    ),
    node,
  )
for node in getInventoryList(omit_asset_increase=1, **local_inventory_params):
  addAccountProps(
    (
      ('initial_credit_balance', -(getTotalPrice(node))),
    ),
    node,
  )
# }}}

# payable / receivable accounts {{{
found_balance=False
if account_type_to_group_by_mirror_section_previous_period:
  if src__:
    src_list.append('-- payable / receivable accounts')
  # initial balance
  local_inventory_params = {
    'node_uid': getAccountUidListByCategory(
      category=account_type_to_group_by_mirror_section_previous_period,
      strict_membership=1,
    ),
    'group_by_mirror_section': 1,
  }
  for node in getInventoryList(
        to_date=period_start_date,
        portal_type=accounting_movement_type_list + balance_movement_type_list,
        **local_inventory_params
      ):
    total_price = getTotalPrice(node)
    addAccountProps(
      (
        ('initial_debit_balance', max(total_price, 0)),
        ('initial_credit_balance', max(-total_price, 0)),
      ),
      node,
      mirror_section=node['mirror_section_uid'] if expand_accounts else MARKER,
    )
  # Balance Transactions
  for node in getInventoryList(
        from_date=from_date,
        at_date=from_date + 1,
        portal_type=balance_movement_type_list,
        **local_inventory_params
      ):
    total_price = getTotalPrice(node)
    addAccountProps(
      (
        ('initial_debit_balance', max(total_price, 0)),
        ('initial_credit_balance', max(-total_price, 0)),
      ),
      node,
      mirror_section=node['mirror_section_uid'] if expand_accounts else MARKER,
    )
    found_balance=True
period_movement_type_list = accounting_movement_type_list
if not found_balance:
  period_movement_type_list += balance_movement_type_list
if expand_accounts:
  if src__:
    src_list.append('-- expand_accounts')
  local_inventory_params = {
    'node_uid': node_uid_of_strict_account_type_to_group_by_mirror_section,
    'group_by_mirror_section': 1,
    'from_date': period_start_date,
    'to_date': from_date,
    'portal_type': period_movement_type_list,
  }
  for node in getInventoryList(omit_asset_decrease=1, **local_inventory_params):
    addAccountProps(
      (
        ('initial_debit_balance', getTotalPrice(node)),
      ),
      node,
      mirror_section=node['mirror_section_uid'],
    )
  for node in getInventoryList(omit_asset_increase=1, **local_inventory_params):
    addAccountProps(
      (
        ('initial_credit_balance', -(getTotalPrice(node))),
      ),
      node,
      mirror_section=node['mirror_section_uid'],
    )
# }}}

# bank accounts {{{
if node_uid_of_strict_account_type_to_group_by_payment:
  if src__:
    src_list.append('-- bank accounts')
  # Initial balance
  local_inventory_params = {
    'node_uid': node_uid_of_strict_account_type_to_group_by_payment,
    'group_by_payment': 1,
  }
  for node in getInventoryList(
        to_date=period_start_date,
        portal_type=accounting_movement_type_list + balance_movement_type_list,
        **local_inventory_params
      ):
    total_price = getTotalPrice(node)
    addAccountProps(
      (
        ('initial_debit_balance', max(total_price, 0)),
        ('initial_credit_balance', max(-total_price, 0)),
      ),
      node,
      payment=node['payment_uid'],
    )
  found_balance = False
  # Balance Transaction
  for node in getInventoryList(
        from_date=from_date,
        at_date=from_date + 1,
        portal_type=balance_movement_type_list,
        **local_inventory_params
      ):
    account_props = getAccountProps(node, payment=node['payment_uid'])
    total_price = (getTotalPrice(node)) + account_props.get('initial_debit_balance', 0) - account_props.get('initial_credit_balance', 0)
    account_props['initial_debit_balance'] = max(total_price, 0)
    account_props['initial_credit_balance'] = max(- total_price, 0)
    found_balance = True
  period_movement_type_list = accounting_movement_type_list
  if not found_balance:
    period_movement_type_list += balance_movement_type_list
  local_inventory_params = {
    'node_uid': node_uid_of_strict_account_type_to_group_by_payment,
    'group_by_payment': 1,
    'from_date': period_start_date,
    'to_date': from_date,
    'portal_type': period_movement_type_list,
  }
  for node in getInventoryList(omit_asset_decrease=1, **local_inventory_params):
    addAccountProps(
      (
        ('initial_debit_balance', getTotalPrice(node)),
      ),
      node,
      payment=node['payment_uid'],
    )
  for node in getInventoryList(omit_asset_increase=1, **local_inventory_params):
    addAccountProps(
      (
        ('initial_credit_balance', -(getTotalPrice(node))),
      ),
      node,
      payment=node['payment_uid'],
    )
# }}}

if src__:
  return src_list

TRANSLATED_NONE = Base_translateString('None')

node_title_and_id_cache = {}
def getNodeTitleAndId(node_relative_url):
  try:
    return node_title_and_id_cache[node_relative_url]
  except KeyError:
    node = traverse(node_relative_url)
    return node_title_and_id_cache.setdefault(
      node_relative_url,
      (
        node.getUid(),
        node.getTranslatedTitle(),
        node.Account_getGapId(gap_root=selected_gap),
        node.getProperty('string_index'),
        node,
      )
    )

section_price_currency_dict = {None: ''}
def getSectionPriceCurrencyFromSectionUid(uid):
  if uid is MARKER:
    return ''
  try:
    return section_price_currency_dict[uid]
  except KeyError:
    price_currency = ''
    brain_list = portal_catalog(uid=uid, limit=2)
    if brain_list:
      brain, = brain_list
      price_currency = brain.getObject().getProperty('price_currency_reference')
      section_price_currency_dict[uid] = price_currency
    return price_currency

analytic_title_dict = {None: ''}
def getAnalyticTitleFromUid(uid):
  if uid is MARKER:
    return ''
  try:
    return analytic_title_dict[uid]
  except KeyError:
    title = ''
    brain_list = portal_catalog(uid=uid, limit=2)
    if brain_list:
      brain, = brain_list
      node = brain.getObject()
      title = node.getTranslatedTitle()
      reference = node.getReference()
      if reference:
        title = '%s - %s' % (reference, title)
    analytic_title_dict[uid] = title
    return title

mirror_section_title_dict = {None: ''}
def getMirrorSectionTitleFromUid(uid):
  if uid is MARKER:
    return ''
  try:
    return mirror_section_title_dict[uid]
  except KeyError:
    title = ''
    brain_list = portal_catalog(uid=uid, limit=2)
    if brain_list:
      brain, = brain_list
      title = brain.getObject().getTitle()
      mirror_section_title_dict[uid] = title
    return title

payment_title_dict = {None: TRANSLATED_NONE}
def getPaymentTitleFromUid(uid):
  try:
    return payment_title_dict[uid]
  except KeyError:
    title = ''
    brain_list = portal_catalog(uid=uid, limit=2)
    if brain_list:
      brain, = brain_list
      title = brain.getObject().getTitle()
      payment_title_dict[uid] = title
    return title

line_list = []
for key, data in six.iteritems(line_per_account):
  node_relative_url = key[0]
  mirror_section_uid = key[1]
  payment_uid = key[2]
  analytic_key_list = key[3:]

  mirror_section_title = None
  if expand_accounts:
    mirror_section_title = getMirrorSectionTitleFromUid(mirror_section_uid)

  node_uid, node_title, node_id, node_string_index, node = getNodeTitleAndId(node_relative_url)

  if selected_gap and not node.isMemberOf(selected_gap):
    continue

  if payment_uid is not MARKER:
    node_title += " (%s)" % getPaymentTitleFromUid(payment_uid)

  if not node_string_index:
    node_string_index = '%-10s' % node_id

  initial_debit_balance = data.get('initial_debit_balance', 0)
  initial_credit_balance = data.get('initial_credit_balance', 0)

  total_initial_debit_balance += round(initial_debit_balance, precision)
  total_initial_credit_balance += round(initial_credit_balance, precision)
  final_debit_balance = round(initial_debit_balance + data['debit'], precision)
  final_credit_balance = round(initial_credit_balance + data['credit'], precision)
  closing_balance = final_debit_balance - final_credit_balance
  total_final_balance_if_debit += round(max(closing_balance, 0), precision)
  total_final_balance_if_credit += round(max(-closing_balance, 0) or 0, precision)

  line = Object(
    uid='new_',
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
    final_balance_if_credit=max(-closing_balance, 0) or 0,
  )

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
  line_list = [
    line for line in line_list
    if line['debit'] or
       line['credit'] or
       line['initial_credit_balance'] or
       line['initial_debit_balance']
  ]
line_list.sort(key=lambda obj: obj['sort_key'])

# cache values for stat
request.set('TrialBalance.total_initial_debit_balance', total_initial_debit_balance)
request.set('TrialBalance.total_initial_credit_balance', total_initial_credit_balance)
request.set('TrialBalance.debit', total_debit)
request.set('TrialBalance.credit', total_credit)
request.set('TrialBalance.final_balance_if_debit', total_final_balance_if_debit)
request.set('TrialBalance.final_balance_if_credit', total_final_balance_if_credit)

if per_account_class_summary:
  current_gap = selected_gap or portal.portal_preferences.getPreferredAccountingTransactionGap() or ''
  if current_gap.startswith('gap/'):
    current_gap = current_gap[4:]
  def getAccountClass(account_relative_url):
    account = traverse(account_relative_url)
    for gap in account.getGapList():
      if gap.startswith(current_gap):
        gap_part_list = gap.split('/')
        # TODO: this should not be ID
        # country / accounting principle / ${class}
        if len(gap_part_list) > 2:
          return gap_part_list[2]
    return None # this account has no class on the current GAP

  account_per_class = {}
  for brain in line_list:
    account_per_class.setdefault(getAccountClass(brain.node_relative_url), []).append(brain)

  line_list = []
  add_line = line_list.append
  for account_class in sorted(account_per_class):
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
    add_line(Object(
      node_title=Base_translateString(
        'Total for class ${account_class}',
        mapping={'account_class': account_class or '???'},
      ),
      initial_balance=round(initial_debit_balance - initial_credit_balance, precision),
      initial_debit_balance=round(initial_debit_balance, precision),
      debit=round(debit, precision),
      final_debit_balance=round(final_debit_balance, precision),
      initial_credit_balance=round(initial_credit_balance, precision),
      credit=round(credit, precision),
      final_credit_balance=round(final_credit_balance, precision),
      final_balance_if_debit=round(final_balance_if_debit, precision),
      final_balance_if_credit=round(final_balance_if_credit, precision),
      final_balance=round(final_debit_balance - final_credit_balance, precision),
    ))

    add_line(Object(node_title=' '))

return line_list
# vim: foldmethod=marker
