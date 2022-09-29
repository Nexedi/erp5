from Products.ERP5Form.Report import ReportSection

report_section_list = []

for section_info in context.TaxReturn_getSectionInformationList():
  section_title = section_info['section_title']
  selection_params = section_info['selection_params']
  selection_params['section_title'] = section_title
  report_section_list.append(ReportSection(
      path=context.getPhysicalPath(),
      form_id='TaxReturn_viewSummaryReportSection',
      selection_name='tax_return_summary_report_section_selection',
      selection_params=selection_params))

return report_section_list
