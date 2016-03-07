date = context.getStartDate()

if not date:
  return ""
else:
  return context.Base_translateString(date.Day())
