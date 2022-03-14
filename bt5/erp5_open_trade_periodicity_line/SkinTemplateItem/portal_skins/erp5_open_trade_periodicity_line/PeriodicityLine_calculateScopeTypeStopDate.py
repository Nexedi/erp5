if scope_type=='until_the_next_period':
  return context.getNextPeriodicalDate(start_date)
elif scope_type=='until_the_end_of_month':
  def getNextMonth(year, month):
    """
    Returns year and month integer values of next month.
    """
    if month==12:
      return year+1, 1
    else:
      return year, month+1

  def getLastDayOfMonth(year, month):
    """
    Returns last day of month.
    """
    next_month_year, next_month_month = getNextMonth(year, month)
    datetime = DateTime(next_month_year, next_month_month, 1)-1
    return datetime.day()

  def getEndOfMonth(date):
    """
    Returns the end of month.
    """
    year = date.year()
    month = date.month()
    day = getLastDayOfMonth(year, month)
    return DateTime(year, month, day)
  return getEndOfMonth(start_date)

raise ValueError('Unknown scope type: %s' % scope_type)
