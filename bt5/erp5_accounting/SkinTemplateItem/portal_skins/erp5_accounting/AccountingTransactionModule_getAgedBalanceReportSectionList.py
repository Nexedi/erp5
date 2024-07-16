import six
from Products.ERP5Type.Message import translateString
from Products.ERP5Form.Report import ReportSection

def translate(*args, **kw):
  return six.text_type(translateString(*args, **kw))

request = container.REQUEST
section_category = request['section_category']
section_category_strict = request['section_category_strict']
simulation_state = request['simulation_state']
account_type = request['account_type']
period_list = [int(period) for period in request['period_list']]
at_date = (request.get("at_date") or DateTime()).latestTime()
detailed = request['detailed']

selection_columns = [('mirror_section_title', 'Third Party'), ]
if detailed:
  selection_columns.extend([
                     ('explanation_title', 'Title'),
                     ('gap_id', 'Account Number'),
                     ('reference', 'Invoice Number'),
                     ('specific_reference', 'Transaction Reference'),
                     ('date', 'Operation Date'),
                     ('portal_type', 'Transaction Type'), ])
selection_columns.extend([
                     ('total_price', 'Balance'),
                     ('period_future', 'Future'), ] )

editable_columns = [('date', 'date'), ('period_future', 'period_future'),
                    ('total_price', 'total_price')]

previous_period = 0
for idx, period in enumerate(period_list):
  if idx != 0:
    previous_period = period_list[idx - 1]
  selection_columns.append(('period_%s' % idx, translate(
      'Period ${period_number} (from ${from} to ${to} days)',
      mapping={'period_number': 1 + idx,
               'from': previous_period,
               'to': period} )))
  editable_columns.append(('period_%s' % idx, ''))

selection_columns.append(('period_%s' % (idx + 1),
  translate('Older (more than ${day_count} days)',
   mapping={'day_count': period_list[-1]})))
editable_columns.append(('period_%s' % (idx + 1), ''))

selection_params = dict(section_category=section_category,
                        section_category_strict=section_category_strict,
                        account_type=account_type,
                        editable_columns=editable_columns,
                        simulation_state=simulation_state,
                        period_list=period_list,
                        at_date=at_date)

ledger = request.get('ledger', None)
if ledger:
  selection_params['ledger'] = ledger

return [ReportSection(form_id=(detailed and
                               'AccountingTransactionModule_viewDetailedAgedBalanceReportSection' or
                               'AccountingTransactionModule_viewSummaryAgedBalanceReportSection'),
                      path=context.getPhysicalPath(),
                      selection_columns=selection_columns,
                      selection_name=(detailed and
                                      'accounting_transaction_module_detailed_aged_balance_selection' or
                                      'accounting_transaction_module_summary_aged_balance_selection'),
                      selection_params=selection_params)]
