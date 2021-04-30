from Products.ERP5Type.Core.Workflow import ValidationFailed
from Products.ERP5Type.Message import translateString

closing_period = state_change['object']
valid_state_list = ['started', 'stopped', 'delivered']

closing_period.Base_checkConsistency()

start_date = closing_period.getStartDate()
stop_date = closing_period.getStopDate()

if start_date > stop_date:
  raise ValidationFailed(translateString("Start date is after stop date."))

period_list = [
    x
    for x in closing_period.getParentValue().contentValues(
        portal_type="Accounting Period",
        checked_permission="Access contents information",
    )
    if x.getSimulationState() in valid_state_list
]

for period in period_list:
  if start_date <= period.getStopDate() and not stop_date <= period.getStartDate():
    raise ValidationFailed(translateString(
        "${date} is already in an open accounting period.",
        mapping={'date': start_date}))

previous_period = next(
    iter(
        sorted(
            [x for x in period_list if x != closing_period],
            key=lambda p: p.getStartDate(),
            reverse=True,
        )
    ),
    None,
)
if previous_period is not None:
  if (start_date - previous_period.getStopDate()) > 1.9:
    raise ValidationFailed(translateString(
        "Last opened period ends on ${last_openned_date},"+
        " this period starts on ${this_period_start_date}."+
        " Accounting Periods must be consecutive.",
          mapping = { 'last_openned_date': previous_period.getStopDate(),
                      'this_period_start_date': start_date } ))
