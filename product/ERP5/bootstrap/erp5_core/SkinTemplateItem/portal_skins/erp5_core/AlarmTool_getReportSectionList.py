"""
  Returns a list of all alarms in
  the form of report sections.

  TODO: cache this result in RAM
  on a per transaction level.
"""
REQUEST = context.REQUEST
if display_success is None: display_success = REQUEST.form.get('display_success')
if display_raw_result is None: display_raw_result = REQUEST.form.get('display_raw_result')

from Products.ERP5Form.Report import ReportSection
result = []

for alarm in context.contentValues():
  if alarm.isEnabled() and \
    (display_success or alarm.sense()) and\
    (display_raw_result or alarm.getReportMethodId()):
    if alarm.getReportMethodId():
      form_id = alarm.getReportMethodId()
    else:
      form_id = 'Alarm_viewReport'
    result.append(
      ReportSection(
        title=alarm.getTitle(),
        path=alarm.getPhysicalPath(),
        level=1,
        form_id=form_id,
        listbox_display_mode='FlatListMode')
      )

return result
