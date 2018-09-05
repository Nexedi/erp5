"""
================================================================================
Create the actual report and return parameters for the report header
================================================================================
"""
# parameters
# ------------------------------------------------------------------------------
#

def translateText(snip):
  return rep_localiser.erp5_ui.gettext(snip, lang=rep_language).encode('utf-8').strip()

rep = context
rep_language = rep.getLanguage() if getattr(rep, 'getLanguage', None) else None
rep_localiser = rep.getPortalObject().Localizer
rep_data_source_caller = None

rep_start_date = kwargs.get('start_date', None)
rep_stop_date = kwargs.get('stop_date', None)
rep_title = kwargs.get('report_title')

# bridge for filling in testdata and setting exported title to bogus dates
if kwargs.get('override_batch_mode'):
  rep_data_source_caller = getattr(context, "PaySheetTransaction_getPayslipTestData", None)
  rep_start_date = DateTime("1976-11-04")
  rep_stop_date = DateTime("1976-11-30")

if rep_data_source_caller is None:
  rep_data_source_caller = getattr(context, "PaySheetTransaction_getPayslipTestData")
  rep_start_date = rep_start_date or context.Base_getFirstAndLastDayOfMonth(day="first")
  rep_stop_date = rep_stop_date or context.Base_getFirstAndLastDayOfMonth(day="last")

kwargs["report_data"] = rep_data_source_caller(start_date=rep_start_date,stop_date=rep_stop_date)

rep_content = context.Person_generatePayslipReportContent(*args, **kwargs)

if isinstance(rep_content, unicode):
  rep_content = rep_content.encode("utf8")

return rep_content, rep_title, ' '.join([
  translateText("from").title(),
  rep_start_date.strftime('%Y/%m/%d'),
  translateText("to"),
  rep_stop_date.strftime('%Y/%m/%d')
])
