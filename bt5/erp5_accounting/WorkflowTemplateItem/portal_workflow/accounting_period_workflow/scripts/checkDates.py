from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import translateString

closing_period = state_change['object']
valid_state_list = ['started', 'stopped', 'delivered']

closing_period.Base_checkConsistency()

start_date = closing_period.getStartDate()
stop_date = closing_period.getStopDate()

if start_date > stop_date:
  raise ValidationFailed(translateString("Start date is after stop date."))

period_list = closing_period.getParentValue().searchFolder(
                              simulation_state=valid_state_list,
                              sort_on=[('delivery.start_date', 'asc')],
                              portal_type='Accounting Period')

for period in period_list:
  period = period.getObject()
  if period.getSimulationState() in valid_state_list:
    if start_date <= period.getStopDate() and not stop_date <= period.getStartDate():
      raise ValidationFailed(translateString(
          "${date} is already in an open accounting period.",
          mapping={'date': start_date}))

if len(period_list) > 1:
  last_period  = period_list[-1].getObject()
  if last_period.getId() == closing_period.getId():
    last_period  = period_list[-2].getObject()
  if (start_date - last_period.getStopDate()) > 1:
    raise ValidationFailed(translateString(
        "Last opened period ends on ${last_openned_date},"+
        " this period starts on ${this_period_start_date}."+
        " Accounting Periods must be consecutive.",
          mapping = { 'last_openned_date': last_period.getStopDate(),
                      'this_period_start_date': start_date } ))
