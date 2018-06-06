enrollment_record = context.Person_getCareerRecord('DSN Enrollment Record')

if dsn_report is None:
  dsn_report = context

result = {
  'person': dsn_report.DSNMonthlyReport_getDataDict(block_id='S21.G00.30', target=context, enrollment_record=enrollment_record),
  'contract': dsn_report.DSNMonthlyReport_getDataDict(block_id='S21.G00.40', target=context.getDefaultCareerValue(), enrollment_record=enrollment_record),
  'person_relative_url': context.getRelativeUrl(),
  'enrollment_record': enrollment_record,
  'seniority': dsn_report.DSNMonthlyReport_getDataDict(block_id='S21.G00.86', target=context, enrollment_record=enrollment_record),
}

return result
