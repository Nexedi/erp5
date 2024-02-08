import six
from Products.ZSQLCatalog.SQLCatalog import ComplexQuery, SimpleQuery
import six

kw["report_data"] = context.PaySheetTransaction_getPayslipData()
kw["report_data"]["amount_of_remuneration_evolution"] = context.REQUEST.get('field_your_evoluation_remuneration', 0)


node_uid = context.getSourceSectionUid()
from_date = context.getStartDate()
at_date = context.getStopDate().latestTime()

year_before = DateTime(at_date.year() - 1, 12, 31)

total_holiday_year_before = context.portal_simulation.getInventory(
  portal_type="Holiday Acquisition",
  node_uid= node_uid,
  at_date = year_before.latestTime(),
  simulation_state='confirmed'
)

total_holiday_this_year = context.portal_simulation.getInventory(
  portal_type="Holiday Acquisition",
  node_uid= node_uid,
  at_date = at_date,
  from_date = DateTime(at_date.year(), 1, 1 ),
  simulation_state='confirmed'
)

total_holiday_taken = context.portal_simulation.getInventory(
  portal_type = "Leave Request Period",
  node_uid = node_uid,
  simulation_state = "confirmed",
  effective_date = SimpleQuery(effective_date=at_date, comparison_operator='<='))

# total_holiday_taken is negatif
total_holiday_year_before += total_holiday_taken

if total_holiday_year_before < 0:
  total_holiday_this_year += total_holiday_year_before
  total_holiday_year_before = 0


taken_holiday = context.portal_simulation.getInventory(
  portal_type = "Leave Request Period",
  node_uid = node_uid,
  simulation_state = "confirmed",
  effective_date = ComplexQuery(
    SimpleQuery(effective_date=from_date, comparison_operator='>='),
    SimpleQuery(effective_date=at_date, comparison_operator='<='),
    logical_operator='AND'
  ))

kw["report_data"]["total_holiday_this_year"] = total_holiday_this_year
kw["report_data"]["total_holiday_year_before"] = total_holiday_year_before

kw["report_data"]["taken_holiday"] = abs(taken_holiday)

if batch:
  return kw

rep_content = context.PaySheetTransaction_generatePayslipReportContent(**kw)

if six.PY2 and isinstance(rep_content, six.text_type):
  rep_content = rep_content.encode("utf8")

return rep_content,"",""
