if kw.get("delivery.start_date"):
  return context.searchFolder(*args, **kw)
import DateTime
dt = DateTime.DateTime() - 60
kw["delivery.start_date"] = ">= " + dt.Date()
return context.searchFolder(*args, **kw)
