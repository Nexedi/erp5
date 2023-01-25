"""Get the report sections for general ledger
"""
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery
from Products.ERP5Form.Report import ReportSection
portal   = context.portal_url.getPortalObject()
request  = portal.REQUEST

cat_tool = portal.portal_categories
Base_translateString = portal.Base_translateString

at_date             = request['at_date'].latestTime()
section_category    = request['section_category']
section_uid = context.Base_getSectionUidListForSectionCategory(
                        section_category, request['section_category_strict'])
simulation_state    = request['simulation_state']
hide_analytic  = request['hide_analytic']
from_date           = request.get('from_date', None)
mirror_section_category_list = request.get('mirror_section_category_list',
                                            None)
mirror_section = request.get('mirror_section', None)

gap_list = []
for gap in request.get('gap_list', ()):
  # XXX the field should maybe use base=1 on the category, but it is also used in other contexts
  gap_list.append('gap/%s' % gap)

period_start_date = context\
    .Base_getAccountingPeriodStartDateForSectionCategory(
          section_category=section_category, date=from_date or at_date)
gap_root = request.get('gap_root')


export = request['export']
if export:
  request.set('merge_report_section_list', 1)

# currency precision
currency = portal.Base_getCurrencyForSection(request['section_category'])
precision = portal.account_module.getQuantityPrecisionFromResource(currency)
request.set('precision', precision)

# There are some disabled fields in Account_viewAccountingTransactionList based on this condition.
request.other['is_accounting_report'] = True

params = dict(precision=precision,
              section_uid=section_uid,
              simulation_state=simulation_state,
              )
project = request.get('project')
if project:
  if project == 'None':
    params['project_uid'] = SimpleQuery(project_uid=None)
  else:
    params['project_uid'] = portal.portal_categories.restrictedTraverse(project).getUid()

funding_category = request.get('funding')
if funding_category:
  if funding_category == 'None':
    params['funding_uid'] = SimpleQuery(funding_uid=None)
  else:
    funding_value = portal.restrictedTraverse(funding_category, None)
    if funding_value is not None and funding_value.getPortalType() != 'Category':
      params['funding_uid'] = funding_value.getUid()
    else:
      params['funding_category'] = funding_category

function_category = request.get('function')
if function_category:
  if function_category == 'None':
    params['function_uid'] = SimpleQuery(function_uid=None)
  else:
    function_value = portal.restrictedTraverse(function_category, None)
    if function_value is not None and function_value.getPortalType() != 'Category':
      params['function_uid'] = function_value.getUid()
    else:
      params['function_category'] = function_category

if mirror_section:
  mirror_section_uid = portal.restrictedTraverse(mirror_section).getUid()
  params['mirror_section_uid'] = mirror_section_uid

ledger = request.get('ledger', None)
if ledger:
  if not isinstance(ledger, list):
    # Allows the generation of reports on different ledgers as the same time
    ledger = [ledger]
  ledger_value_list = [cat_tool.restrictedTraverse(ledger_category, None)
                       for ledger_category in ledger]
  for ledger_value in ledger_value_list:
    params.setdefault('ledger_uid', []).append(ledger_value.getUid())

default_selection_params = params.copy()
default_selection_params['period_start_date'] = period_start_date
default_selection_params['movement_portal_type'] = portal.getPortalAccountingMovementTypeList()
default_selection_params['no_mirror_section_uid_cache'] = 1


# if user request report without grouping reference, don't show accounts that only have grouped lines in the period.
if request.get('omit_grouping_reference', False):
  if at_date:
    params['grouping_query'] = portal.ERP5Site_getNotGroupedAtDateSQLQuery(at_date)
  else:
    params['grouping_reference'] = None
  default_selection_params['omit_grouping_reference'] = True

analytic_column_list = ()
if hide_analytic:
  default_selection_params['group_by'] = ( 'explanation_uid',
                                           'mirror_section_uid',
                                           'payment_uid' )
else:
  analytic_column_list = context.accounting_module.AccountModule_getAnalyticColumnList()
request.set('analytic_column_list', analytic_column_list) # for Movement_getExplanationTitleAndAnalytics

account_columns = (
  ('date', 'Operation Date'),
  ('Movement_getSpecificReference', 'Transaction Reference'),
  ('mirror_section_title', 'Third Party'),
  ('Movement_getExplanationTitleAndAnalytics', 'Title\nReference and Analytics' if analytic_column_list else 'Title\nReference'),
  ('debit_price', 'Debit'),
  ('credit_price', 'Credit'),
  ('running_total_price', 'Running Balance'),
  ('grouping_reference', 'Grouping Reference'),
  ('grouping_date', 'Grouping Date'),
  ('getTranslatedSimulationStateTitle', 'State'),
)
# export mode have a different layout
if export:
  account_columns = context.AccountModule_getGeneralLedgerColumnItemList()

# utility functions
traverse = portal.restrictedTraverse
account_name_cache = {}
def getAccountName(account_relative_url):
  try:
    return account_name_cache[account_relative_url]
  except KeyError:
    name = traverse(account_relative_url).Account_getFormattedTitle(gap_root=gap_root)
    account_name_cache[account_relative_url] = name
    return name


title_for_uid_cache = {None: ''}
def getTitleForUid(uid):
  try:
    return title_for_uid_cache[uid]
  except KeyError:
    name = ''
    brain_list = portal.portal_catalog(uid=uid, limit=2)
    if brain_list:
      brain, = brain_list
      name = brain.getObject().getTitle()
    title_for_uid_cache[uid] = name
    return name

def getFullAccountName(account_info):
  account_relative_url, mirror_section_uid, payment_uid = account_info
  account_name = getAccountName(account_relative_url)
  mirror_section_name = getTitleForUid(mirror_section_uid)
  if mirror_section_name:
    account_name = '%s (%s)' % (account_name, mirror_section_name)
  payment_name = getTitleForUid(payment_uid)
  if payment_name:
    account_name = '%s (%s)' % (account_name, payment_name)
  return account_name

def addReportSection(**kw):
  kw.setdefault('form_id', 'Account_viewAccountingTransactionList')
  kw.setdefault('selection_name', 'account_preference_selection')
  kw.setdefault('selection_columns', account_columns)
  kw.setdefault('listbox_display_mode', 'FlatListMode')
  title = kw['title']
  if export: # in export more we do not insert report sections headers and use
             # a list view form
    kw.pop('title')
    kw['form_id'] = 'Account_viewAccountingTransactionListExport'
  report_section_list.append((title, ReportSection(**kw)))

# look at inventories to decide which sections will be shown
balance_sheet_account_type_list = [c[0] for c in
 cat_tool.account_type.asset.getCategoryChildItemList(base=1, is_self_excluded=False, display_none_category=False ) + \
 cat_tool.account_type.equity.getCategoryChildItemList(base=1, is_self_excluded=False, display_none_category=False) + \
 cat_tool.account_type.liability.getCategoryChildItemList(base=1, is_self_excluded=False, display_none_category=False) ]

profit_and_loss_account_type = []
for account_type_value in (cat_tool.account_type.expense,
                     cat_tool.account_type.income):
  profit_and_loss_account_type.extend(
      [category.getRelativeUrl() for category in
        account_type_value.getIndexableChildValueList()])

account_type_to_group_by_payment = [ 'account_type/asset/cash/bank' ]

account_type_to_group_by_mirror_section = [
                  'account_type/asset/receivable',
                  'account_type/liability/payable', ]

account_type_to_group_by_node = [at for at in balance_sheet_account_type_list
  if at not in account_type_to_group_by_payment
  and at not in account_type_to_group_by_mirror_section]

if gap_list or gap_root:
  params['node_category'] = gap_list or gap_root

if mirror_section_category_list:
  params['mirror_section_category'] = mirror_section_category_list
  default_selection_params['mirror_section_category'] =\
        mirror_section_category_list

# inventory parameters for the total section
total_params = default_selection_params.copy()
# we'll append all the node used, instead of using node_category.
total_params['node_uid'] = set([])

report_section_list = []

existing_section_dict = {}

# group by node
# movements in the period
for inventory in portal.portal_simulation.getInventoryList(
                            node_category_strict_membership=account_type_to_group_by_node,
                            portal_type=portal.getPortalAccountingMovementTypeList(),
                            from_date=from_date,
                            at_date=at_date,
                            group_by_node=1,
                            group_by_section=0,
                            group_by_mirror_section=0,
                            group_by_resource=0,
                            **params):
  key = (inventory.node_relative_url, None, None)
  existing_section_dict[key] = True

  selection_params = default_selection_params.copy()
  selection_params['from_date'] = from_date
  selection_params['at_date'] = at_date
  selection_params['node_uid'] = inventory.node_uid
  selection_params['payment_uid'] = None
  selection_params.setdefault('mirror_section_uid', None)
  addReportSection(path=inventory.node_relative_url,
                   selection_params=selection_params,
                   title=getFullAccountName(key))
  total_params['node_uid'].add(inventory.node_uid)

# non zero balance at begining of period
for inventory in portal.portal_simulation.getInventoryList(
                            node_category_strict_membership=account_type_to_group_by_node,
                            portal_type=portal.getPortalAccountingMovementTypeList(),
                            at_date=from_date,
                            group_by_node=1,
                            group_by_section=0,
                            group_by_mirror_section=0,
                            group_by_resource=0,
                            **params):
  key = (inventory.node_relative_url, None, None)
  if key in existing_section_dict:
    continue
  if not inventory.total_price:
    continue
  existing_section_dict[key] = True

  selection_params = default_selection_params.copy()
  selection_params['from_date'] = from_date
  selection_params['at_date'] = at_date
  selection_params['node_uid'] = inventory.node_uid
  selection_params['payment_uid'] = None
  selection_params.setdefault('mirror_section_uid', None)
  addReportSection(path=inventory.node_relative_url,
                   selection_params=selection_params,
                   title=getFullAccountName(key))
  total_params['node_uid'].add(inventory.node_uid)


# profit & loss -> same, but from date limited to the current period
for inventory in portal.portal_simulation.getInventoryList(
                            node_category_strict_membership=profit_and_loss_account_type,
                            portal_type=portal.getPortalAccountingMovementTypeList(),
                            from_date=max(from_date, period_start_date),
                            at_date=at_date,
                            group_by_node=1,
                            group_by_section=0,
                            group_by_mirror_section=0,
                            group_by_resource=0,
                            **params):
  key = (inventory.node_relative_url, None, None)
  selection_params = default_selection_params.copy()
  selection_params['from_date'] = max(from_date, period_start_date)
  selection_params['at_date'] = at_date
  selection_params['period_start_date'] = max(from_date, period_start_date)
  selection_params['node_uid'] = inventory.node_uid
  selection_params['payment_uid'] = None
  selection_params.setdefault('mirror_section_uid', None)
  addReportSection(path=inventory.node_relative_url,
                   selection_params=selection_params,
                   title=getFullAccountName(key))
  total_params['node_uid'].add(inventory.node_uid)

# group by mirror_section
# movements in the period
for inventory in portal.portal_simulation.getInventoryList(
                            node_category_strict_membership=account_type_to_group_by_mirror_section,
                            portal_type=portal.getPortalAccountingMovementTypeList(),
                            from_date=from_date,
                            at_date=at_date,
                            group_by_node=1,
                            group_by_section=0,
                            group_by_mirror_section=1,
                            group_by_resource=0,
                            **params):
  key = (inventory.node_relative_url, inventory.mirror_section_uid, None)
  existing_section_dict[key] = True

  selection_params = default_selection_params.copy()
  selection_params['from_date'] = from_date
  selection_params['at_date'] = at_date
  selection_params['node_uid'] = inventory.node_uid
  selection_params['payment_uid'] = None
  selection_params['mirror_section_uid'] = inventory.mirror_section_uid or SimpleQuery(mirror_section_uid=None)
  addReportSection(path=inventory.node_relative_url,
                   selection_params=selection_params,
                   title=getFullAccountName(key))
  total_params['node_uid'].add(inventory.node_uid)

# non zero balance at begining of period
for inventory in portal.portal_simulation.getInventoryList(
                            node_category_strict_membership=account_type_to_group_by_mirror_section,
                            portal_type=portal.getPortalAccountingMovementTypeList(),
                            at_date=from_date,
                            group_by_node=1,
                            group_by_section=0,
                            group_by_mirror_section=1,
                            group_by_resource=0,
                            **params):
  key = (inventory.node_relative_url, inventory.mirror_section_uid, None)

  if key in existing_section_dict:
    continue
  if not inventory.total_price:
    continue
  existing_section_dict[key] = True

  selection_params = default_selection_params.copy()
  selection_params['from_date'] = from_date
  selection_params['at_date'] = at_date
  selection_params['node_uid'] = inventory.node_uid
  selection_params['payment_uid'] = None
  selection_params['mirror_section_uid'] = inventory.mirror_section_uid or SimpleQuery(mirror_section_uid=None)
  addReportSection(path=inventory.node_relative_url,
                   selection_params=selection_params,
                   title=getFullAccountName(key))
  total_params['node_uid'].add(inventory.node_uid)

# group by payment
# movements in the period
for inventory in portal.portal_simulation.getInventoryList(
                            node_category_strict_membership=account_type_to_group_by_payment,
                            portal_type=portal.getPortalAccountingMovementTypeList(),
                            from_date=from_date,
                            at_date=at_date,
                            group_by_node=1,
                            group_by_section=0,
                            group_by_payment=1,
                            group_by_resource=0,
                            **params):
  key = (inventory.node_relative_url, None, inventory.payment_uid)
  existing_section_dict[key] = True

  selection_params = default_selection_params.copy()
  selection_params['from_date'] = from_date
  selection_params['at_date'] = at_date
  selection_params['node_uid'] = inventory.node_uid
  selection_params['payment_uid'] = inventory.payment_uid or SimpleQuery(payment_uid=None)
  selection_params.setdefault('mirror_section_uid', None)
  addReportSection(path=inventory.node_relative_url,
                   selection_params=selection_params,
                   title=getFullAccountName(key))
  total_params['node_uid'].add(inventory.node_uid)

# non zero balance at begining of period
for inventory in portal.portal_simulation.getInventoryList(
                            node_category_strict_membership=account_type_to_group_by_payment,
                            portal_type=portal.getPortalAccountingMovementTypeList(),
                            at_date=from_date,
                            group_by_node=1,
                            group_by_section=0,
                            group_by_payment=1,
                            group_by_resource=0,
                            **params):
  key = (inventory.node_relative_url, None, inventory.payment_uid)
  if key in existing_section_dict:
    continue
  if not inventory.total_price:
    continue
  existing_section_dict[key] = True

  selection_params = default_selection_params.copy()
  selection_params['from_date'] = from_date
  selection_params['at_date'] = at_date
  selection_params['node_uid'] = inventory.node_uid
  selection_params['payment_uid'] = inventory.payment_uid or SimpleQuery(payment_uid=None)
  selection_params.setdefault('mirror_section_uid', None)
  addReportSection(path=inventory.node_relative_url,
                   selection_params=selection_params,
                   title=getFullAccountName(key))
  total_params['node_uid'].add(inventory.node_uid)


report_section_list = [x[1] for x in sorted(report_section_list, key=lambda x: x[0])]

if not export:
  total_params['at_date'] = at_date
  total_params['node_uid'] = list(total_params['node_uid'])
  report_section_list.append(ReportSection(
              path=context.getPhysicalPath(),
              title=Base_translateString("Total"),
              form_id='AccountModule_viewGeneralLedgerSummary',
              selection_name='accounting_report_selection',
              selection_params=total_params))

return report_section_list
