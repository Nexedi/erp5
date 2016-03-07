# Returns the total price declared as immobilised for all aggregated items
from DateTime import DateTime

millis = DateTime('2000/01/01 12:00:00.001') - DateTime('2000/01/01 12:00:00')

self = context
stop_date = self.getStopDate() + millis
if stop_date is None:
  return None
item_list = []
for line in self.contentValues():
  try:
    item_list += line.getAggregateValueList()
  except:
    pass
price = 0
for item in item_list:
  try:
    price += item.getLastImmobilisationInitialPrice(at_date=stop_date, **kw)
  except:
    pass
return price
