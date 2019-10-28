from Products.ERP5Form.Report import ReportSection
request = container.REQUEST

if context.getSourcePayment():
  # As we are showing quantities and not asset prices, we use the precision
  # from this bank account currency.
  request.set('precision',
      context.getQuantityPrecisionFromResource(
        context.getSourcePaymentValue().getPriceCurrency()))

report_section_list = [
  ReportSection(form_id='BankReconciliation_view',
                path=context.getPhysicalPath()),
]

if request.get('show_reconcilied', True):
  report_section_list.append(
    ReportSection(form_id='BankReconciliation_viewBankReconciliationReportSection',
                  path=context.getPhysicalPath(),
                  selection_name="bank_reconciliation_report_selection",
                  selection_params={'title': 'Reconciled Transactions',
                                    'mode': 'unreconcile'}))
if request.get('show_non_reconcilied', True):
  report_section_list.append(
    ReportSection(form_id='BankReconciliation_viewBankReconciliationReportSection',
                  selection_name="bank_reconciliation_report_selection",
                  path=context.getPhysicalPath(),
                  selection_params={'title': 'Not Reconciled Transactions',
                                    'mode': 'reconcile'}))

return report_section_list
