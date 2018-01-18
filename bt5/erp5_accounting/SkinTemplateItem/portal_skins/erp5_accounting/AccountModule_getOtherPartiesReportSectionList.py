"""Client & vendors accounts.
"""
portal = context.portal_url.getPortalObject()

from Products.ERP5Form.Report import ReportSection

request = context.REQUEST
at_date = request['at_date'].latestTime()
section_category = request['section_category']
simulation_state = request['simulation_state']
role_filter_list = request.get('mirror_section_category_list', None)
omit_balanced_accounts = request['omit_balanced_accounts']
from_date = request.get('from_date', None)
project = request.get('project', None)
ledger = request.get('ledger', None)

currency = portal.Base_getCurrencyForSection(request['section_category'])
precision = portal.account_module.getQuantityPrecisionFromResource(currency)
request.set('precision', precision)

request.other['is_accounting_report'] = True

# role_filter_list == None means no filter on the role
if role_filter_list == [''] :
  role_filter_list = None

section_uid = context.Base_getSectionUidListForSectionCategory(
    request['section_category'],
    request['section_category_strict'])
result = []

params =  {
    'at_date': at_date,
    'section_uid': section_uid,
    'simulation_state': simulation_state
}

if from_date:
  params['from_date'] = from_date
else :
  params['no_from_date'] = 1

if project:
  if project == 'None':
    params['project_uid'] = project
  else:
    params['project_uid'] = portal.restrictedTraverse(project).getUid()

if ledger:
  if not isinstance(ledger, list):
    # Allows the generation of reports on different ledgers as the same time
    ledger = [ledger]
  portal_categories = portal.portal_categories
  ledger_value_list = [portal_categories.restrictedTraverse(ledger_category, None)
                       for ledger_category in ledger]
  for ledger_value in ledger_value_list:
    params.setdefault('ledger_uid', []).append(ledger_value.getUid())

simulation_tool = portal.portal_simulation

entity_columns = [
    ('date', 'Date'),
    ('Movement_getExplanationTranslatedPortalType', 'Type'),
    ('Movement_getNodeGapId', 'GAP'),
    ('Movement_getExplanationReference', 'Invoice No'),
    ('Movement_getExplanationTitle', 'Title'),
    ('Movement_getSpecificReference', 'Reference'),
    ('getTranslatedSimulationStateTitle', 'State'),
    ('debit_price', 'Debit'),
    ('credit_price', 'Credit'),
    ('running_total_price', 'Balance'),
]

if not request['omit_grouping_reference']:
  entity_columns.append(('grouping_reference',
                         'Grouping Reference'))


# TODO: this can be a simple getInventoryList with mirror section category
# (role)
for party in context.Account_zDistinctSectionList(
                              section_uid=section_uid,
                              at_date=at_date):
  o = party.getObject()
  keep_this_one = True
  if role_filter_list:
    keep_this_one = False
    for role in role_filter_list:
      if role and o.isMemberOf(role):
        keep_this_one = True
        break

  if not keep_this_one:
    continue

  if o.getPortalType() == 'Person' or\
      not o.isMemberOf(section_category):
        # don't show entities belonging to the group we are reporting
    if omit_balanced_accounts and (
        round(simulation_tool.getInventoryAssetPrice(
                    mirror_section_uid=party.uid,
                    ignore_unknown_columns=True,
                    precision=precision,
                    node_category_strict_membership=(
                          'account_type/asset/receivable',
                          'account_type/liability/payable'),
                    **params
                    ), precision) == 0.):
      pass
    else:
      title = o.getTitle()
      if o.getProperty('role', None):
        title += ' (%s)' % o.getRoleTranslatedTitle()
      result.append(
                 ReportSection(title=title,
                               level=1,
                               path=o.getPhysicalPath(),
                               form_id='Entity_viewAccountingTransactionList',
                               selection_name='other_parties_report_selection',
                               selection_params=params,
                               selection_columns=entity_columns,
                               selection_sort_order=[('stock.date', 'ascending'),
                                                      ('stock.uid', 'ascending'),],))

return result
