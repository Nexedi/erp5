"""
Script that returns the list of diff of 2 historical states of ERP5 object(s).

This should is used as a 'list method' as it returns a list of temp base object
which have its properties as : `path` and `diff`.
"""
from Products.ERP5Type.Document import newTempBase

portal =  context.getPortalObject()
portal_diff = portal.portal_diff
request = context.REQUEST
object_revision_list = []
history_size = portal.portal_preferences.getPreferredHtmlStyleZodbHistorySize()

# In case the request has been made via action on any ERP5 object, we get the
# paths as `your_<field_name>` as this is what use as field in dialog. Hence,
# its better to check for path in the request also.
if first_path is None:
  first_path = request.get('your_first_path', None)
if second_path is None:
  second_path = request.get('your_second_path', None)

# Case I: When we try to access the dialog directly from `portal_diff` or from
# selections in a module. If the paths are None, then return an empty list
# or try to get the paths from selection and then return the diff.
if first_path is None and second_path is None:
  list_selection_name = request.get('list_selection_name', None)
  # In case the list_selection_name is there, it can be the case of selection
  # from the module, hence we get the paths from the selection and use them to
  # create diff.
  if list_selection_name is not None:
    selected_obj_list = portal.portal_selections.getSelectionCheckedValueList(selection_name=list_selection_name)
    object_revision_list.extend(selected_obj_list)
  else:
    # Return an empty list here. This would be the case when we first access
    # the dialog and then it try to get list of items to dipslay on the listbox
    return []

# Case II: Get object revision from the date of the revisions.
# The default dates for revision are the 1st and 2nd
# revision dates.
if first_date not in (None, ''):
  first_obj = portal.restrictedTraverse(first_path)
  old_state_revision = context.Base_getRevisionFromDate(first_obj, first_date)
  object_revision_list.append(old_state_revision)
if second_date not in (None, ''):
  second_obj = portal.restrictedTraverse(second_path)
  new_state_revision = context.Base_getRevisionFromDate(second_obj, second_date)
  object_revision_list.append(new_state_revision)

# Case III: When the paths exist, but there is no revision given
# for the paths, we diff the current revision
if first_path != second_path:
  # Diff the current verison if both the paths are different
  if first_path is not None and first_date in (None, ''):
    object_revision_list.append(portal.restrictedTraverse(first_path))
  if second_path is not None and second_date in (None, ''):
    object_revision_list.append(portal.restrictedTraverse(second_path))
else:
  # If both the paths are same, diff between the current version
  # and the last version(if it exists)
  # Get the historical revisions for the object and check if there
  # is more than one revision
  obj = portal.restrictedTraverse(first_path)
  revision_date_list = obj.Base_getRevisionDateList(obj, size=history_size)
  if len(revision_date_list) > 1:
    object_revision_list.append(obj.Base_getRevisionFromDate(obj, revision_date_list[1]))
    object_revision_list.append(obj.Base_getRevisionFromDate(obj, revision_date_list[0]))

# Use DiffTool to get the diff between the 2 objects in object_revision_list List.
# These 2 objects can be revisions of same object, 2 different revisions of
# different objects or 2 current ERP5 object.
if len(object_revision_list) > 1:
  # Using this last 2 Historical revision dicts, create a Diff
  diff_list = portal_diff.diffPortalObject(object_revision_list[0], object_revision_list[1]).asBeautifiedJSONDiff()
  # Return a list of TempBase objects which can be displayed in a listbox
  uid = 1
  tempbase_list = []
  for diff_unit in diff_list:
    temp_obj = newTempBase(portal,
                           diff_unit['path'],
                           **diff_unit)
    temp_obj.setUid(uid)
    uid = uid + 1
    tempbase_list.append(temp_obj)

  return tempbase_list

return []
