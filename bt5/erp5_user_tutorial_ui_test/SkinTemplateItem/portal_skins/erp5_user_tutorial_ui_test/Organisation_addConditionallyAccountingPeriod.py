my_organisation = context
real_organisation = my_organisation.Organisation_getMappingRelatedOrganisation()

# conditionally add accounting period
used_test_date = DateTime('%s/01/01' % context.Zuite_getHowToInfo()['now'].strftime('%Y')).earliestTime()
found_period = False
for accounting_period in real_organisation.contentValues(portal_type='Accounting Period'):
  if accounting_period.getSimulationState() == 'started':
    if accounting_period.getStartDate().earliestTime() <= used_test_date <= accounting_period.getStopDate().latestTime():
      found_period = True
      break
if not found_period:
  test_accounting_period = real_organisation.newContent(
    portal_type = 'Accounting Period',
    title = context.Zuite_getHowToInfo()['optional_new_accounting_period_title'],
    start_date = used_test_date - 1,
    stop_date = used_test_date + 3650
  )
  test_accounting_period.start()
