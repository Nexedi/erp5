from Products.ERP5Type.DateUtils import addToDate
Base_translateString = context.Base_translateString

task_portal_type = 'Task'
task_module = context.getDefaultModule(task_portal_type)

def validateDay(date):
  if (periodicity_month_day_list in ([], None, ())):
    return 1
  elif len(periodicity_month_day_list) > 0:
    return date.day() in periodicity_month_day_list

def validateWeek(date):
  if (periodicity_week_day_list in ([], None, ())) and \
     (periodicity_week_list is None):
    return 1
  if periodicity_week_day_list not in (None, (), []):
    if not (date.Day() in periodicity_week_day_list):
      return 0
  if periodicity_week_list not in (None, (), []):
    if not (date.week() in periodicity_week_list):
      return 0
  return 1

def validateMonth(date):
  if (periodicity_month_list in ([], None, ())):
    return 1
  elif len(periodicity_month_list) > 0:
    return date.month() in periodicity_month_list

def getNextPeriodicalDate(current_date):
  next_start_date = current_date
  previous_date = next_start_date
  next_start_date = addToDate(next_start_date, day=1)
  while 1:
    if (validateDay(next_start_date)) and \
       (validateWeek(next_start_date)) and \
       (validateMonth(next_start_date)):
      break
    else:
      next_start_date = addToDate(next_start_date, day=1)
  return next_start_date

def getDatePeriodList(start_date):
  result = []
  # First date has to respect the periodicity config
  next_start_date = getNextPeriodicalDate(start_date)
  while (next_start_date is not None) and \
    (next_start_date <= periodicity_stop_date):
    result.append(next_start_date)
    next_start_date = getNextPeriodicalDate(next_start_date)
  return result


start_date = context.getStartDate()
if start_date is None:
  return context.Base_redirect(
    'view',
    keep_items={'portal_status_message': Base_translateString(
      'Tasks can not be created, start date is empty.'
    )})
else:
  date_list = getDatePeriodList(start_date)
  for next_date in date_list:
    context.activate(activity="SQLQueue").Task_duplicate(next_date)
  return context.Base_redirect(
    'view',
    keep_items={'portal_status_message': Base_translateString(
      '${count} tasks created.', mapping={'count':len(date_list)}
    )})
