"""
This script gets 2 ERP5 objects based on the parameters provided, either by
using path and datetime or by using context and serial and then creates a
diff between the 2 objects.

The diff returned is a list of Tempbase object with properties `path` and `diff`.
"""
from Products.ERP5Type.Document import newTempBase
from ZODB.POSException import ConflictError
from zExceptions import Unauthorized

portal =  context.getPortalObject()
portal_diff = portal.portal_diff
request = context.REQUEST
object_revision_list = []
history_size = portal.portal_preferences.getPreferredHtmlStyleZodbHistorySize()
Base_translateString = context.Base_translateString

first_obj = None
second_obj = None

# In case the request has been made via action on any ERP5 object, we get the
# paths as `your_<field_name>` as this is what use as field in dialog. Hence,
# its better to check for path in the request also.
if first_path is None:
  first_path = request.get('your_first_path', None)
if second_path is None:
  second_path = request.get('your_second_path', None)

# If first_path and second_path exists, get their current revision from ZODB
if first_path not in (None, ''):
  first_obj = portal.restrictedTraverse(first_path)
if second_path not in (None, ''):
  second_obj = portal.restrictedTraverse(second_path)

# Try to get the objects from the serial. In case of serial, we will use the
# context as the base object.
if serial:
  if not first_obj:
    first_obj = context
  try:
    context.HistoricalRevisions[serial]
  except (ConflictError, Unauthorized):
    raise
  except Exception:
    return [newTempBase(portal, Base_translateString('Historical revisions are'
                        ' not available, maybe the database has been packed'))]
  first_obj = context.HistoricalRevisions[serial]

if next_serial:
  if next_serial == '0.0.0.0':
    second_obj = context
  else:
    if not second_obj:
      second_obj = context
    second_obj = context.HistoricalRevisions[next_serial]

# Here if the datetime and the paths exist in params, we always give priority
# to get the objects via these params.

if (first_obj is not None and (first_obj == second_obj)):
  # If both the objects are same, diff between the current version
  # and the last version(if it exists)
  # Get the historical revisions for the object and check if there
  # is more than one revision
  revision_date_list = first_obj.Base_getRevisionDateList(first_obj, size=history_size)
  if len(revision_date_list) > 1:
    first_obj = first_obj.Base_getRevisionFromDate(first_obj, revision_date_list[1])
    second_obj = second_obj.Base_getRevisionFromDate(second_obj, revision_date_list[0])

# Get object revision from the date of the revisions.
# The default dates for revision are the 1st and 2nd
# revision dates.
if first_date not in (None, ''):
  first_obj = context.Base_getRevisionFromDate(first_obj, first_date)
if second_date not in (None, ''):
  second_obj = context.Base_getRevisionFromDate(second_obj, second_date)

# When we try to access the dialog directly from `portal_diff` or from
# selections in a module. If the paths are None, then return an empty list
# or try to get the paths from selection and then return the diff.
if ((first_path is None and second_path is None) and
    (first_obj is None and second_obj is None)):
  # Make sure to always check if the first_obj and second_obj is empty, because this script
  # is used outside of Diff Tool also, where we might have list_selection_name which will
  # end up getting useless selection.
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
