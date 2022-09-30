# This is what we want to display in the report
# project_month     worker1    worker2    worker3
#    january           34              32             15
#    february          10              14             20

def getYearAndMonth(date):
  if date is None:
    return(None,None)
  return (date.year(),date.Month())


def getMonthDict(line):
  start_date = line.getStartDate()
  stop_date = line.getStopDate()
  month_dict={}
  if getYearAndMonth(start_date) == getYearAndMonth(stop_date):
    month_dict={getYearAndMonth(start_date):line.getQuantity() or 0}
  else:
    nb_days = (stop_date-start_date)*86400
    current_date = start_date
    previous_current_date = start_date
    quantity = line.getQuantity() or 0
    while current_date < stop_date:
      previous_current_date = current_date
      year_and_month = getYearAndMonth(current_date)
      while previous_current_date.month()==current_date.month() and current_date < stop_date:
        current_date = current_date + 1
      month_dict[year_and_month] = quantity / nb_days * (current_date-previous_current_date) * 86400


  return month_dict

def getTotalQuantity(line,worker):
  quantity = {}
  child_list = line.objectValues()
  if len(child_list)>0:
    for child in child_list:
      child_quantity = getTotalQuantity(child,worker)
      for key,value in child_quantity.items():
        if key not in quantity:
          quantity[key] = 0
        quantity[key] = quantity[key] + value
  else:
    if worker in line.getSourceValueList() or (line.getSourceValue() is None and worker is None):
      quantity = getMonthDict(line)
  return quantity

listbox = []
worker_list = context.getSourceValueList() + [None]
worker_quantity = {}
for worker in worker_list:
  worker_quantity[worker] = getTotalQuantity(context,worker)

month_list = []
current_date = context.getStartDate()
month_list.append(getYearAndMonth(current_date))
from DateTime import DateTime
while getYearAndMonth(current_date)!=getYearAndMonth(context.getStopDate()):
  start_date_day = context.getStartDate().day()
  previous_current_date = current_date
  current_date = current_date + 1
  while current_date.day() != start_date_day and current_date-previous_current_date<31:
    current_date = current_date + 1
  month_list.append(getYearAndMonth(current_date))

month_list.append((None,None))
total_dict = {}
total_dict['year'] = 'Total'
total_dict['month'] = 'Total'
for year,month in month_list:
  listbox_line = {}
  listbox_line['year'] = year
  listbox_line['month'] = month
  for worker in worker_list:
    quantity = 0
    if (year,month) in worker_quantity[worker]:
      quantity = worker_quantity[worker][(year,month)]
    worker_title = 'unknown'
    if worker is not None:
      worker_title = worker.getTitle()
    total_dict[worker_title] = total_dict.get(worker_title,0) + quantity
    listbox_line[worker_title] = quantity
  listbox.append(listbox_line)
listbox.append(total_dict)



context.Base_updateDialogForm(listbox=listbox)

return context.Project_viewQuantityReportDialog(listbox=listbox)
