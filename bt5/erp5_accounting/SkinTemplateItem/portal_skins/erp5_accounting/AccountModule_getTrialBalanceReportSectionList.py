""" Trial balance.
"""
from Products.ERP5Form.Report import ReportSection

request = context.REQUEST
portal  = context.portal_url.getPortalObject()

at_date  = request['at_date']
from_date = request.get('from_date', None)
portal_type = request.get('portal_type', None)
function = request.get('function', None)
funding = request.get('funding', None)
ledger = request.get('ledger', None)
project = request.get('project', None)
simulation_state = request['simulation_state']
expand_accounts = request.get('expand_accounts', False)
show_empty_accounts = request['show_empty_accounts']
per_account_class_summary = request['per_account_class_summary']
gap_root = request.get('gap_root', None)
mirror_section_category = request.get('mirror_section_category_list', None)
show_detailed_balance_columns = request['show_detailed_balance_columns']
section_uid = portal.Base_getSectionUidListForSectionCategory(
                                   request['section_category'],
                                   request['section_category_strict'])

period_start_date = portal.Base_getAccountingPeriodStartDateForSectionCategory(
       section_category=request['section_category'], date=from_date or at_date)
# for the report summary
request.set('period_start_date', period_start_date)

if not from_date:
  from_date = period_start_date

# currency precision
currency = portal.Base_getCurrencyForSection(request['section_category'])
precision = portal.account_module.getQuantityPrecisionFromResource(currency)
request.set('precision', precision)


# optional GAP filter
node_uid = []
gap_uid_list = []
for gap in request.get('gap_list', ()):
  gap_uid_list.append(portal.portal_categories.gap.restrictedTraverse(gap).getUid())
if gap_uid_list:
  node_uid = [x.uid for x in portal.portal_catalog(
                                   portal_type='Account',
                                   default_gap_uid=gap_uid_list)] or -1

request.set('is_accounting_report', True)
group_analytic = request.get('group_analytic', ())
group_analytic_uid = ()

extra_columns = ()
if expand_accounts:
  extra_columns += ('mirror_section_title', 'Third Party'),

possible_analytic_column_list = context.AccountModule_getAnalyticColumnList()
for analytic in group_analytic:
  if analytic == 'project':
    extra_columns += (('project_uid', 'Project', ), )
    group_analytic_uid += ('project_uid',)
  elif analytic == 'function':
    extra_columns += (('function_uid',
        context.AccountingTransactionLine_getFunctionBaseCategoryTitle()),)
    group_analytic_uid += ('function_uid',)
  elif analytic == 'funding':
    extra_columns += (('funding_uid',
        context.AccountingTransactionLine_getFundingBaseCategoryTitle()),)
    group_analytic_uid += ('funding_uid',)
  elif analytic == 'section':
    extra_columns += (('section_uid', 'Section'), ('Movement_getSectionPriceCurrency', 'Accounting Currency'))
    group_analytic_uid += ('section_uid',)
  else:
    for analytic_column in possible_analytic_column_list:
      if analytic_column[0] == analytic:
        uid_key = 'strict_%s' % analytic_column[0].replace('_translated_title', '_uid')
        group_analytic_uid += (uid_key, )
        extra_columns += ((uid_key, analytic_column[1]),)


if show_detailed_balance_columns:
  selection_columns = (
    ('node_id', 'GAP Account ID'),
    ('node_title', 'Account Name'),
  ) + extra_columns + (
    ('initial_debit_balance', 'Initial Debit Balance'),
    ('initial_credit_balance', 'Initial Credit Balance'),
    ('initial_balance', 'Initial Balance'),
    ('debit', 'Debit Transactions'),
    ('credit', 'Credit Transactions'),
    ('final_debit_balance', 'Final Debit Balance'),
    ('final_credit_balance', 'Final Credit Balance'),
    ('final_balance', 'Final Balance'),
    ('final_balance_if_debit', 'Final Balance (Debit)'),
    ('final_balance_if_credit', 'Final Balance (Credit)'),
  )
else:
  selection_columns = (
    ('node_id', 'GAP Account ID'),
    ('node_title', 'Account Name'),
  ) + extra_columns + (
    ('initial_balance', 'Initial Balance'),
    ('debit', 'Debit Transactions'),
    ('credit', 'Credit Transactions'),
    ('final_balance', 'Final Balance'),
  )

return [ ReportSection(
            path=portal.account_module.getPhysicalPath(),
            form_id='AccountModule_viewAccountListForTrialBalance',
            selection_name='trial_balance_selection',
            selection_columns=selection_columns,
            selection_params=dict(show_empty_accounts=show_empty_accounts,
                                  expand_accounts=expand_accounts,
                                  at_date=at_date.latestTime(),
                                  from_date=from_date.earliestTime(),
                                  period_start_date=
                                          period_start_date.earliestTime(),
                                  section_uid=section_uid,
                                  function=function,
                                  funding=funding,
                                  ledger=ledger,
                                  project=project,
                                  portal_type=portal_type,
                                  simulation_state=simulation_state,
                                  precision=precision,
                                  group_analytic=group_analytic_uid,
                                  node_uid=node_uid,
                                  mirror_section_category=
                                          mirror_section_category,
                                  per_account_class_summary=
                                          per_account_class_summary,
                                  gap_root=gap_root,
                                  show_detailed_balance_columns=show_detailed_balance_columns), )]
