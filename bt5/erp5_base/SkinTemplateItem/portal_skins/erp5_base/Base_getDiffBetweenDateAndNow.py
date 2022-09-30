if not date:
  return ''
try:
  now =  DateTime()
  date = DateTime(date)
except Exception:
  return ''
Base_translateString = context.Base_translateString
diff = now - date
if diff < 1:
  hours = diff*24.0
  if hours < 1:
    minutes = hours*60.0
    if minutes < 1:
      seconds = minutes*60.0
      if seconds < 1:
        return Base_translateString('Now')
      if 2 > seconds > 1:
        return Base_translateString('${timedif} second ago', mapping={'timedif':int(seconds)})
      return Base_translateString('${timedif} seconds ago', mapping={'timedif':int(seconds)})
    if 2 > minutes > 1:
      return Base_translateString('${timedif} minute ago', mapping={'timedif':int(minutes)})
    return Base_translateString('${timedif} minutes ago', mapping={'timedif':int(minutes)})
  if 2 > hours > 1:
    return Base_translateString('${timedif} hour ago', mapping={'timedif':int(hours)})
  return Base_translateString('${timedif} hours ago', mapping={'timedif':int(hours)})
else:
  if diff > 365.25:
    return Base_translateString('More than 1 year')
  elif diff > 30:
    return Base_translateString('More than 1 month')
  elif 2 > diff > 1:
    return Base_translateString('Yesterday')
  return Base_translateString('${timedif} days ago', mapping={'timedif':int(diff)})
