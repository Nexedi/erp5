from DateTime import DateTime

current_date_string = DateTime().strftime('%Y-%m-%d')
start_date = DateTime('%s 00:00' % current_date_string)
stop_date = DateTime('%s 23:59' % current_date_string)
context.setStartDate(start_date)
context.setStopDate(stop_date)
