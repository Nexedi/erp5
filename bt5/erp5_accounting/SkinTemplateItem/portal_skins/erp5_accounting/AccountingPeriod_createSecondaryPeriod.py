from DateTime import DateTime
from erp5.component.module.DateUtils import addToDate
from Products.ERP5Type.Message import translateString

month_added = 1
if frequency == 'quarterly':
  month_added = 3

date = context.getStartDate()
while date < context.getStopDate():
  end_date = addToDate(date, dict(month=month_added))
  # recreate a DateTime to have it in the proper timezone
  start_date = DateTime(date.year(), date.month(), date.day())
  stop_date = DateTime((end_date - 1).year(),
                       (end_date - 1).month(),
                       (end_date - 1).day())

  period = context.newContent(portal_type='Accounting Period',
                              start_date=start_date,
                              stop_date=stop_date)

  if frequency == 'quarterly':
    period.setShortTitle('%s-%s' % (
      start_date.strftime('%Y %m'), (end_date - 1).strftime('%m')))
  else:
    period.setShortTitle(start_date.strftime('%Y-%m'))
    period.setTitle(str(translateString(start_date.strftime('%B'))))

  if open_periods:
    period.start()

  date = end_date

return context.Base_redirect(form_id,
     keep_items=dict(portal_status_message=translateString('Accounting periods created.')))
