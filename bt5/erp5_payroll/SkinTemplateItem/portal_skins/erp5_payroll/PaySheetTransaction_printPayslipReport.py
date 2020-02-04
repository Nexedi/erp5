"""
================================================================================
Wire PaySheetTransaction through to erp5_corporate_identity Report
================================================================================
"""
# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin

# parameters   (* default)
# ------------------------------------------------------------------------------
# format:                   output in html*, pdf
# international_form        translate terms
# language                  target_language

return context.Base_printAsReport(
  format=format,
  report_title="Payslip",
  report_name = "PaySheetTransaction_generatePayslipReport",
  language=target_language,
  start_date=context.getStartDate() or None,
  stop_date=context.getStopDate() or None,
  **kw
)
