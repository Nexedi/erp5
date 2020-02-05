kw["report_data"] = context.PaySheetTransaction_getPayslipData()
rep_content = context.PaySheetTransaction_generatePayslipReportContent(**kw)

if isinstance(rep_content, unicode):
  rep_content = rep_content.encode("utf8")

return rep_content,"",""
