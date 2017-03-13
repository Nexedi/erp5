"""Get the report sections for account statement.
Account is the combination of :
   - node (the Account in account module)
   - mirror_section (the Entity in organisation / person module)
   - payment (the Bank account for the organisation)
"""

from Products.ERP5Form.Report import ReportSection
from Products.ERP5Type.Message import translateString
request = context.REQUEST
traverse = context.getPortalObject().portal_categories.restrictedTraverse

# for preference info fields on Account_viewAccountingTransactionList
request.set('is_accounting_report', True)

at_date = request['at_date']
section_uid = context.Base_getSectionUidListForSectionCategory(
                                             request['section_category'],
                                             request['section_category_strict'])
# XXX for now node is required (ie. we cannot display all transactions with
# a third party regardless of the account).
node = request['node']
mirror_section = request.get('mirror_section', None)
payment = request.get('payment', None)
function = request.get('function', None)
funding = request.get('funding', None)
ledger = request.get('ledger', None)
project = request.get('project', None)
simulation_state = request['simulation_state']
hide_analytic = request['hide_analytic']
from_date = request.get('from_date', None)
detailed_from_date_summary = request.get('detailed_from_date_summary', 0)
omit_grouping_reference = request.get('omit_grouping_reference', 0)
parent_portal_type = request.get('portal_type')
period_start_date = context\
    .Base_getAccountingPeriodStartDateForSectionCategory(
                   section_category=request['section_category'],
                   date=from_date or at_date)

export = request['export']

# Also get the currency, to know the precision
currency = context.Base_getCurrencyForSection(request['section_category'])
precision = context.account_module.getQuantityPrecisionFromResource(currency)
# we set the precision in request, for formatting on editable fields
request.set('precision', precision)

params = dict(at_date=at_date,
              period_start_date=period_start_date,
              section_uid=section_uid,
              node_uid=traverse(node).getUid(),
              simulation_state=simulation_state,
              detailed_from_date_summary=detailed_from_date_summary,
              omit_grouping_reference=omit_grouping_reference,
              from_date=None,
              payment_uid=None,
              mirror_section_uid=None,)

if from_date:
  params['from_date'] = from_date
if payment:
  if payment == 'None':
    params['payment_uid'] = payment
  else:
    params['payment_uid'] = traverse(payment).getUid()
if project:
  if project == 'None':
    params['project_uid'] = project
  else:
    params['project_uid'] = traverse(project).getUid()
if function:
  function_value = traverse(function, None)
  if function_value is not None and function_value.getPortalType() != 'Category':
    params['function_uid'] = function_value.getUid()
  else:
    params['function_category'] = function
if funding:
  funding_value = traverse(funding, None)
  if funding_value is not None and funding_value.getPortalType() != 'Category':
    params['funding_uid'] = funding_value.getUid()
  else:
    params['funding_category'] = funding
if mirror_section:
  params['mirror_section_uid'] = traverse(mirror_section).getUid()
if parent_portal_type:
  params['parent_portal_type'] = parent_portal_type
if ledger:
  params['ledger'] = ledger

analytic_column_list = ()
if hide_analytic:
  params['group_by'] = ( 'explanation_uid',
                         'mirror_section_uid',
                         'payment_uid', )
else:
  analytic_column_list = context.AccountModule_getAnalyticColumnList()
  params['analytic_column_list'] = analytic_column_list
request.set('analytic_column_list', analytic_column_list) # for Movement_getExplanationTitleAndAnalytics

selection_columns = (
  ('date', 'Operation Date'),
  ('Movement_getSpecificReference', 'Transaction Reference'),
  ('mirror_section_title', 'Third Party'),
  ('Movement_getExplanationTitleAndAnalytics', 'Title\nReference and Analytics' if analytic_column_list else 'Title\nReference'),
)
if len(section_uid) > 1:
  selection_columns += (('section_title', 'Section'),)
selection_columns += (
  ('debit_price', 'Debit'),
  ('credit_price', 'Credit'),
  ('running_total_price', 'Running Balance'),
  ('grouping_reference', 'Grouping Reference'),
  ('grouping_date', 'Grouping Date'),
  ('getTranslatedSimulationStateTitle', 'State'),
)

if export:
  selection_columns = context.AccountModule_getGeneralLedgerColumnItemList()

report_section_list = []
if from_date and detailed_from_date_summary:
  report_section_list.append(
    ReportSection(form_id='', level=4,
                  title=translateString('Not Grouped Lines in Beginning Balance')))

  report_section_list.append(
    ReportSection(
            path=node,
            form_id='Account_viewNotGroupedAccountingTransactionList',
            selection_name='account_preference_selection',
            selection_params=params,
            selection_columns=selection_columns,
            listbox_display_mode='FlatListMode',
            selection_sort_order=[
                        ('stock.date', 'ascending'),
                        ('stock.uid', 'ascending')],))

  report_section_list.append(
    ReportSection(form_id=None, level=4,
                  title=translateString('Lines in the Period')))

report_section_list.append(
    ReportSection(
            path=node,
            form_id='Account_viewAccountingTransactionListExport' if export else 'Account_viewAccountingTransactionList',
            selection_name='account_preference_selection',
            selection_params=params,
            selection_columns=selection_columns,
            listbox_display_mode='FlatListMode',
            selection_sort_order=[
                        ('stock.date', 'ascending'),
                        ('stock.uid', 'ascending')],))

return report_section_list
