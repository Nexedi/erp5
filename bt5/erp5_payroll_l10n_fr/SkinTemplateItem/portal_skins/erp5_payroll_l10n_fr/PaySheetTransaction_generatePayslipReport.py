import six
kw["report_data"] = context.PaySheetTransaction_getPayslipData()
kw["report_data"]["amount_of_remuneration_evolution"] = context.REQUEST.get('field_your_evoluation_remuneration', 0)
kw["report_data"]["total_holiday"] = context.REQUEST.get('field_your_total_holiday', 0)
kw["report_data"]["taken_holiday"] = context.REQUEST.get('field_your_taken_holiday', 0)
rep_content = context.PaySheetTransaction_generatePayslipReportContent(**kw)

if six.py2 and isinstance(rep_content, six.text_type):
  rep_content = rep_content.encode("utf8")

return rep_content,"",""
