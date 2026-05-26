portal = context.getPortalObject()

translateString = context.Base_translateString

preferred_date_order = portal.portal_preferences.getPreferredDateOrder() or 'ymd'
def getOrderedDate(date):
  if date is None:
    return ''
  date_parts = {
    'y': '%04d' % date.year(),
    'm': '%02d' % date.month(),
    'd': '%02d' % date.day(),
  }
  return '/'.join([date_parts[part] for part in preferred_date_order])

return [
  (
    translateString("[${date}] ${title} (${amount})", mapping={
      "date": getOrderedDate(x.getStopDate()),
      "title": x.getTitle(),
      "amount": x.getQuantity(),
    }),
    x.getUid(),
  )
  for x in context.objectValues()]
