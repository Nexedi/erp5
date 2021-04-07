assignment = state_change['object']
from DateTime import DateTime
current_date = DateTime()
if assignment.getStopDate() is None or assignment.getStopDate() > current_date:
  assignment.setStopDate(current_date)
