"""
This script gets 2 ERP5 objects based on the parameters provided, either by
using path and datetime or by using context and serial and then creates a
diff between the 2 objects.

The diff returned is a list of Tempbase object with properties `path` and `diff`.
"""
from Products.ERP5Type.Document import newTempBase
from ZODB.POSException import ConflictError
from zExceptions import Unauthorized
from Products.ERP5Type.Log import log

portal =  context.getPortalObject()
portal_diff = portal.portal_diff
request = context.REQUEST
object_revision_list = []
history_size = portal.portal_preferences.getPreferredHtmlStyleZodbHistorySize()
Base_translateString = context.Base_translateString

first_obj = None
second_obj = None

# Try to get the objects from the serial. In case of serial, we will use the
# context as the base object.
if next_serial:
  if next_serial == '0.0.0.0':
    second_obj = context
  else:
    second_obj = context.HistoricalRevisions[next_serial]

if serial:
  try:
    context.HistoricalRevisions[serial]
  except (ConflictError, Unauthorized):
    raise
  except Exception:
    return [newTempBase(portal, Base_translateString('Historical revisions are'
                        ' not available, maybe the database has been packed'))]
  first_obj = context.HistoricalRevisions[serial]

# Here if the datetime and the paths exist in params, we always give priority
# to get the objects via these params.

# In case the request has been made via action on any ERP5 object, we get the
# paths as `your_<field_name>` as this is what use as field in dialog. Hence,
# its better to check for path in the request also.
if first_path is None:
  first_path = request.get('your_first_path', None)
if second_path is None:
  second_path = request.get('your_second_path', None)

if first_path != second_path:
    # Diff the current verison if both the paths are different
  if first_path is not None and first_date in (None, ''):
    first_obj = portal.restrictedTraverse(first_path)
  if second_path is not None and second_date in (None, ''):
    second_obj = portal.restrictedTraverse(second_path)
elif first_path is not None and second_path is not None:
  # If both the paths are same, diff between the current version
  # and the last version(if it exists)
  # Get the historical revisions for the object and check if there
  # is more than one revision
  obj = portal.restrictedTraverse(first_path)
  revision_date_list = obj.Base_getRevisionDateList(obj, size=history_size)
  if len(revision_date_list) > 1:
    first_obj = obj.Base_getRevisionFromDate(obj, revision_date_list[1])
    second_obj = obj.Base_getRevisionFromDate(obj, revision_date_list[0])

# Case II: Get object revision from the date of the revisions.
# The default dates for revision are the 1st and 2nd
# revision dates.
if first_date not in (None, ''):
  obj = portal.restrictedTraverse(first_path)
  first_obj = context.Base_getRevisionFromDate(obj, first_date)
if second_date not in (None, ''):
  obj = portal.restrictedTraverse(second_path)
  second_obj = context.Base_getRevisionFromDate(obj, second_date)

# Case I: When we try to access the dialog directly from `portal_diff` or from
# selections in a module. If the paths are None, then return an empty list
# or try to get the paths from selection and then return the diff.
if ((first_path is None and second_path is None) and
    (first_obj is None and second_obj is None)):
  # XXX: Make sure to always check if the first_obj and second_obj is empty, because this script
  # is more generic(except this case), so there maybe cases where some other
  # list selection might be present for it
  list_selection_name = request.get('list_selection_name', None)
  # In case the list_selection_name is there, it can be the case of selection
  # from the module, hence we get the paths from the selection and use them to
  # create diff.
  if list_selection_name is not None:
    selected_obj_list = portal.portal_selections.getSelectionCheckedValueList(
      selection_name=list_selection_name)
    first_obj = selected_obj_list[0]
    second_obj = selected_obj_list[1]

# Use DiffTool to get the diff between the 2 objects in object_revision_list List.
# These 2 objects can be revisions of same object, 2 different revisions of
# different objects or 2 current ERP5 object.
if first_obj and second_obj:
  # Using this last 2 Historical revision dicts, create a Diff
  diff_list = portal_diff.diffPortalObject(first_obj, second_obj).asBeautifiedJSONDiff()
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
