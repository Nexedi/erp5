from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message
from Products.ERP5Type.DateUtils import getIntervalBetweenDates

if stop_date is None:
  from DateTime import DateTime
  stop_date = DateTime().Date()

resource_title = resource.getTitle()
#context.log("date %s %s" %(start_date, stop_date), "title = %s" %resource_title)

if 'compte' in resource_title:
  interval = getIntervalBetweenDates(start_date,stop_date)
  #context.log("interval", interval)
  if interval['year'] == 3:
    if interval['month'] > 0 or interval["day"] > 0:
      msg = Message(domain='ui', message="Check $check is more than 3 years old.",
                    mapping={"check" : check_nb})
      raise ValidationFailed(msg,)
  elif interval['year'] > 3:
    msg = Message(domain='ui', message="Check $check is more than 3 years old.",
                  mapping={"check" : check_nb})
    raise ValidationFailed(msg,)

elif 'virement' in resource_title:
  interval = getIntervalBetweenDates(start_date, stop_date)
  #context.log("interval", interval)
  if interval['month'] == 3:
    if interval["day"] > 0:
      msg = Message(domain='ui', message="Check $check is more than 3 month old.",
                    mapping={"check" : check_nb})
      raise ValidationFailed(msg,)
  elif interval['month'] > 3 or interval['year'] > 0:
    msg = Message(domain='ui', message="Check $check is more than 3 month old.",
                  mapping={"check" : check_nb})
    raise ValidationFailed(msg,)
