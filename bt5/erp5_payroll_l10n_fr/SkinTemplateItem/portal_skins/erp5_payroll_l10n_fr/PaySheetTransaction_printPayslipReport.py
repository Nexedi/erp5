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

kw['format'] = format
kw['report_header'] = "PaySheetTransaction_generatePayslipReportHeader"
kw['report_name'] = "PaySheetTransaction_generatePayslipReport"
kw['report_footer'] = "PaySheetTransaction_generatePayslipReportFooter"
kw['conversion_dict'] = dict(
  margin_top=60,
  header_spacing=5
)
kw['css_path'] = "payslip_css/payslip"
kw['document_language'] = target_language or 'fr'
kw['start_date'] = context.getStartDate() or None
kw['stop_date'] = context.getStopDate() or None
kw['get_doc_after_save'] = send_to_maileva

if not send_to_maileva:
  return context.Base_printAsReport(**kw)

if not context.Base_isMailevaEnabled():
  return context.Base_redirect('view',
    keep_items={'portal_status_message': 'Maileva is not configured.'})


document = context.Base_printAsReport(**kw)
document.edit(title='BULLETIN DE PAIE: %s' % document.getTitle())

document.PDF_sendToMaileva(recipient=context.getSourceSectionValue(),
                           sender=context.getDestinationTradeValue())
document.setFollowUpValue(context)
document.PDF_setAccountingSecurity()
return document.Base_redirect('PDF_viewPDFJSPreview',
  keep_items={'portal_status_message': 'This document is sending to maileva'})
