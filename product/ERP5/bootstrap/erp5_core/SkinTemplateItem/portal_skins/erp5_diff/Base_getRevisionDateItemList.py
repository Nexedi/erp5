"""
Script to get the list of dates for Historical Revisions for
any object inside ERP5. It is used in the 'items' field for Portal Diff
view for the list field regarding the Dates.

Params:
field_name - Name of the the field which gives us the path
selection_index - Index of the object we want to get from the selection list
                  in case we don't have any path from field
"""
from builtins import str
from DateTime import DateTime

portal = context.getPortalObject()
request = context.REQUEST
date_list = []
history_size = portal.portal_preferences.getPreferredHtmlStyleZodbHistorySize()

# This will be the case when we try to refresh/update the diff, in
# that case we will be getting the second_object_path from the request.
# When we refresh or update the diff, we try to access the value for this field
# in the list method before validation, hence we need it to get it via using
# 'field_<field_name>'
# XXX: Not a good way to get the field value before validation.
path = request.form.get('field_your_%s' % field_name, None)

# If the path is still empty, we try to get it from request
if path is None:
  path  = request.get('your_%s' % field_name, None)

if path :
  # When both paths are same, in case the action call is made
  # from an ERP5 object
  obj = portal.restrictedTraverse(path)
  date_list = obj.Base_getRevisionDateList(obj, size=history_size)

# If there is no path from the field value, then we check for selections
else:
  # In case we are tryng to get the object path from selection,
  # for example when we try to diff 2 objects from one module
  list_selection_name = request.get('list_selection_name')
  # Get the selected values for the web page selection
  if list_selection_name:
    selected_obj_list = portal.portal_selections.getSelectionCheckedValueList(selection_name=list_selection_name)
    obj = selected_obj_list[selection_index]
    date_list = obj.Base_getRevisionDateList(obj, size=history_size)

return [(str(DateTime(date).strftime("%Y-%m-%d %H:%M")), str(date)) for date in date_list]
