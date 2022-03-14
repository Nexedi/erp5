"""
This script returns the default value for second_date field.
"""
from builtins import str
portal = context.getPortalObject()
request = context.REQUEST
history_size = portal.portal_preferences.getPreferredHtmlStyleZodbHistorySize()

first_path = request.get('your_first_path', None)
second_path = request.get('your_second_path', None)
second_date = request.get('your_second_date', None)

if second_date:
  return second_date
# In case both the paths are same, return the 2nd item from the date list.
# This is because its the case where we are trying to diff current and last
# revision of the same object.
elif first_path not in (None, '') and first_path == second_path:
  obj = portal.restrictedTraverse(first_path)
  date_list = obj.Base_getRevisionDateList(obj, size=history_size)
  return str(date_list[1])

return second_date
