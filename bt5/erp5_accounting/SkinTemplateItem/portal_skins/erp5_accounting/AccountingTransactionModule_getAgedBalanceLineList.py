"""
at_date (DateTime)
  See getMovementHistoryList.
section_category (str)
section_category_strict (bool)
  See Base_getSectionUidListForSectionCategory.
  Result passed to getMovementHistoryList.
simulation_state (str or list of str)
  See getMovementHistoryList.
period_list (list of numbers)
  List of operation age ranges, in days. Used to dispatch operations by age:
  period_0: older than earliest period
  period_1: younger than earliest period, older than next period
  ...
  period_n: younger than period n-1, older than at_date
  period_future: Posterior to at_date
account_type (str)
  Must be one of:
    'account_type/asset/receivable'
    'account_type/liability/payable'
lineCallback ((brain, period_name, line_dict) -> dict)
  Called for each line found by getMovementHistoryList.
  brain
    Current line.
  period_name (string)
    Name of the period this line belongs to.
  line_dict (dict)
    Dictionary containing properties of corresponding line in the report.
    May be modified by callback.
  Returned value is resulting line property dictionary, or None to skip this
  row.
reportCallback ((line_list) -> list of dict)
  Called once all lines from getMovementHistoryList have been processed.
  line_list (list)
    Each entry is the dict returned by lineCallback, in order.
    May be modified by callback.
  Returned value is final line list. Each line must be a dict. If unsure, return
  line_list.
"""
from collections import defaultdict
from Products.PythonScripts.standard import Object
if reportCallback is None:
  reportCallback = lambda x: x
portal = context.getPortalObject()
portal_catalog = portal.portal_catalog
portal_categories = portal.portal_categories
# we set the precision in request, for formatting on editable fields
portal.REQUEST.set(
  'precision',
  context.account_module.getQuantityPrecisionFromResource(
    context.Base_getCurrencyForSection(section_category),
  ),
)
line_list = []
assert account_type in ('account_type/asset/receivable', 'account_type/liability/payable')
reverse_price_sign = account_type == 'account_type/liability/payable'
by_mirror_section_list_dict = defaultdict(list)
node_uid_list = [
  x.uid
  for x in portal_catalog(
    portal_type='Account',
    strict_account_type_uid=portal_categories.restrictedTraverse(account_type).getUid(),
  )
]
if not node_uid_list:
  return []
extra_kw = {}
ledger_relative_url_list = kw.get('ledger', None)
if ledger_relative_url_list:
  if not isinstance(ledger_relative_url_list, list):
    ledger_relative_url_list = [ledger_relative_url_list]
  traverse = portal.portal_categories.restrictedTraverse
  extra_kw['ledger_uid'] = [traverse(x).getUid() for x in ledger_relative_url_list]
period_list = [
  ('period_%i' % x, y)
  for x, y in enumerate(sorted(period_list))
]
last_period_id = 'period_%s' % len(period_list)
for brain in portal.portal_simulation.getMovementHistoryList(
  at_date=at_date,
  simulation_state=simulation_state,
  node_uid=node_uid_list,
  portal_type=portal.getPortalAccountingMovementTypeList(),
  section_uid=portal.Base_getSectionUidListForSectionCategory(
    section_category,
    section_category_strict,
  ),
  grouping_query=portal.ERP5Site_getNotGroupedAtDateSQLQuery(at_date),
  **extra_kw
):
  total_price = brain.total_price or 0
  if reverse_price_sign:
    total_price = -total_price
  # Note that we use date_utc because date would load the object and we are just
  # interested in the difference of days.
  age = int(at_date - brain.date_utc)
  if age < 0:
    period_name = 'period_future'
  else:
    for period_name, period in period_list:
      if age <= period:
        break
    else:
      period_name = last_period_id
  line_dict = lineCallback(
    brain=brain,
    period_name=period_name,
    line_dict={
      'mirror_section_uid': brain.mirror_section_uid,
      'total_price': total_price,
      'age': age,
      period_name: total_price,
    },
  )
  if line_dict is not None:
    by_mirror_section_list_dict[brain.mirror_section_uid].append(line_dict)
    line_list.append(line_dict)
if by_mirror_section_list_dict:
  for row in portal_catalog(
    select_list=['title'],
    uid=list(by_mirror_section_list_dict.keys()),
  ):
    title = row.title
    for line in by_mirror_section_list_dict[row.uid]:
      line['mirror_section_title'] = title
return [
  Object(
    uid='new_',
    **x
  )
  for x in reportCallback(line_list)
]
