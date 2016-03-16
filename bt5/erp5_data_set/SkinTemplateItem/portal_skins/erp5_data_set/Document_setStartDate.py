document = context
from DateTime import DateTime
current_date = DateTime()
if document.getStartDate() is None or document.getStartDate() > current_date:
  document.setStartDate(current_date)
