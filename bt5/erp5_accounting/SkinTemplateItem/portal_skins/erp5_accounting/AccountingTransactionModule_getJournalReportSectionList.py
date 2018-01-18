from Products.ERP5Form.Report import ReportSection
request = container.REQUEST
Base_translateString = container.Base_translateString

portal = context.getPortalObject()
# We have to obtain parameters from request because of "generic" implementation
# https://lab.nexedi.com/nexedi/erp5/blob/master/product/ERP5Form/ReportBox.py#L71
portal_type = request['portal_type']
simulation_state = request['simulation_state']
hide_analytic = request['hide_analytic']
project = request.get('project', None)
ledger = request.get('ledger', None)
at_date = request['at_date'].latestTime()
from_date = request.get('from_date') or at_date.earliestTime()
section_uid = context.Base_getSectionUidListForSectionCategory(
                                     request['section_category'],
                                     request['section_category_strict'])
payment_mode = request.get('payment_mode')
payment = request.get('payment')
gap_root = request.get('gap_root')

# Also get the currency, to know the precision
currency = context.Base_getCurrencyForSection(request['section_category'])
precision = context.account_module.getQuantityPrecisionFromResource(currency)
# we set the precision in request, for formatting on editable fields
request.set('precision', precision)

selection_params = dict(portal_type=portal_type,
                        section_uid=section_uid,
                        precision=precision,
                        simulation_state=simulation_state,
                        at_date=at_date,
                        from_date=from_date,
                        payment_mode=payment_mode,
                        gap_root=gap_root,
                        payment=payment)

if project:
  if project == 'None':
    selection_params['project_uid'] = project
  else:
    selection_params['project_uid'] = \
       context.getPortalObject().restrictedTraverse(project).getUid()

if ledger:
  if not isinstance(ledger, list):
    # Allows the generation of reports on different ledgers as the same time
    ledger = [ledger]
  portal_categories = portal.portal_categories
  ledger_value_list = [portal_categories.restrictedTraverse(ledger_category, None)
                       for ledger_category in ledger]
  for ledger_value in ledger_value_list:
    selection_params.setdefault('ledger_uid', []).append(ledger_value.getUid())

analytic_column_list = ()
if hide_analytic:
  selection_params['group_by'] = ( 'explanation_uid',
                                   'mirror_section_uid',
                                   'payment_uid',
                                   'node_uid' )
else:
  analytic_column_list = context.accounting_module.AccountModule_getAnalyticColumnList()
  selection_params['analytic_column_list'] = analytic_column_list

selection_columns = (
    ('specific_reference', 'Transaction Reference'),
    ('date', 'Date'),
    ('title', 'Accounting Transaction Title'),
    ('parent_reference', 'Document Reference'),)
if len(portal_type) > 1:
  selection_columns += (
    ('portal_type', 'Transaction Type'), )
selection_columns += analytic_column_list + (
    ('node_title', 'Account'),
    ('mirror_section_title', 'Third Party'),
    ('debit', 'Debit'),
    ('credit', 'Credit'))

return [ReportSection(
          path=context.getPhysicalPath(),
          title=Base_translateString('Transactions'),
          selection_name='journal_selection',
          form_id='AccountingTransactionModule_viewJournalSection',
          selection_columns=selection_columns,
          selection_params=selection_params)]
