"""
Script that returns the diff of last 2 historical states of the context. This
should be used as a 'list method' as it returns a temp base object which have
its properties as : `path`, `t1` and `t2`
"""
from Products.ERP5Type.Document import newTempBase

portal =  context.getPortalObject()
portal_diff = portal.portal_diff

history = []

# Get the old and new state dates from the dialog submit
new_state_date = kw.get('new_state', None)
old_state_date = kw.get('old_state', None)

# Get object revision from the date of the revisions.
# The default dates for revision are the 1st and 2nd
# revision dates.
if old_state_date is not None:
  old_state = context.Base_getRevisionFromDate(context, old_state_date)
  history.append(old_state)
if new_state_date is not None:
  new_state = context.Base_getRevisionFromDate(context, new_state_date)
  history.append(new_state)

if not history:
  history = context.Base_getZODBChangeHistoryList(context, size=2)

if len(history) > 1:
  # Using this last 2 history dicts, create a Diff
  diff = portal_diff.diffPortalObject(history[0], history[1]).asBeautifiedJSONDiff()
  # Return a list of TempBase objects which can be displayed in a listbox
  tempbase_list = []
  uid = 900
  for x in diff:
    temp_obj = newTempBase(portal,
                          x['path'],
                          **x)
    temp_obj.setUid(int(uid))
    uid = uid + 1
    tempbase_list.append(temp_obj)

  return tempbase_list
