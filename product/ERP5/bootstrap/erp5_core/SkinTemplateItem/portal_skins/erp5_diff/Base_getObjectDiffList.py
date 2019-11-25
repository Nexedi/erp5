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
history_size = portal.portal_preferences.getPreferredHtmlStyleZodbHistorySize()

first_object = None
second_object = None

# In case the request has been made via action on any ERP5 object, we get the
# paths as `your_<field_name>` as this is what use as field in dialog. Hence,
# its better to check for path in the request also.
if first_path is None:
  first_path = request.get('your_first_path', None)
if second_path is None:
  second_path = request.get('your_second_path', None)

# If first_path and second_path exists, get their current revision from ZODB
if first_path not in (None, ''):
  first_object = portal.restrictedTraverse(first_path)
if second_path not in (None, ''):
  second_object = portal.restrictedTraverse(second_path)

# Try to get the objects from the serials.
if first_serial:
  if not first_object:
    first_object = context
  try:
    first_object = first_object.HistoricalRevisions[first_serial]
  except (ConflictError, Unauthorized):
    raise
  except Exception:
    return [newTempBase(portal, context.Base_translateString('Historical revisions are'
                        ' not available, maybe the database has been packed'))]

if second_serial:
  if second_serial == '0.0.0.0':
    # In case the second serial is 0.0.0.0, we should consider the second object as
    # the current version of context
    second_object = context
  else:
    if not second_object:
      second_object = context
    try:
      second_object = second_object.HistoricalRevisions[second_serial]
    except (ConflictError, Unauthorized):
      raise
    except Exception:
      return [newTempBase(portal, context.Base_translateString('Historical revisions are'
                          ' not available, maybe the database has been packed'))]

# Here if the datetime and the paths exist in params, we always give priority
# to get the objects via these params.

if (first_object is not None and (first_object == second_object)):
  # If both the objects are same, diff between the current version
  # and the last version(if it exists)
  # Get the historical revisions for the object and check if there
  # is more than one revision
  revision_date_list = first_object.Base_getRevisionDateList(first_object, size=history_size)
  if len(revision_date_list) > 1:
    first_object = first_object.Base_getRevisionFromDate(first_object, revision_date_list[1])
    second_object = second_object.Base_getRevisionFromDate(second_object, revision_date_list[0])

# Get object revision from the date of the revisions.
# The default dates for revision are the 1st and 2nd
# revision dates.
if first_date not in (None, ''):
  if isinstance(first_object, dict):
    # If the object type is dictionary because historical revisions are present
    # as dictionaries, then we get the object using restrictedTraverse
    first_object = portal.restrictedTraverse(first_path)
  first_object = context.Base_getRevisionFromDate(first_object, first_date)
if second_date not in (None, ''):
  if isinstance(second_object, dict):
    second_object = portal.restrictedTraverse(second_path)
  second_object = context.Base_getRevisionFromDate(second_object, second_date)

# When we try to access the dialog directly from `portal_diff` or from
# selections in a module. If the paths are None, then return an empty list
# or try to get the paths from selection and then return the diff.
if ((first_path is None and second_path is None) and
    (first_object is None and second_object is None)):
  # Make sure to always check if the first_object and second_object is empty, because this script
  # is used outside of Diff Tool also, where we might have list_selection_name which will
  # end up getting useless selection.
  list_selection_name = request.get('list_selection_name', None)
  # In case the list_selection_name is there, it can be the case of selection
  # from the module, hence we get the paths from the selection and use them to
  # create diff.
  if list_selection_name is not None:
    selected_object_list = portal.portal_selections.getSelectionCheckedValueList(
      selection_name=list_selection_name)
    first_object = selected_object_list[0]
    second_object = selected_object_list[1]

# Use DiffTool to get the diff between the 2 objects.
# These 2 objects can be revisions of same object, 2 different revisions of
# different objects or 2 current ERP5 object.
if first_object and second_object:
  diff_list = portal_diff.diffPortalObject(first_object, second_object).asBeautifiedJSONDiff()
  # Return a list of TempBase objects which can be displayed in a listbox
  uid = 1
  tempbase_list = []
  for diff_unit in diff_list:
    temp_object = newTempBase(portal,
                             diff_unit['path'],
                             **diff_unit)
    temp_object.setUid(uid)
    uid = uid + 1
    tempbase_list.append(temp_object)

  return tempbase_list

return []
