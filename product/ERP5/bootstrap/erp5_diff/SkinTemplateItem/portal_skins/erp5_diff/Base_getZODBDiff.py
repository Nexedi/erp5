"""
Script that returns the diff of last 2 historical states of the context. This
should be used as a 'list method' as it returns a temp base object which have
its properties as : `path`, `t1` and `t2`
"""
from Products.ERP5Type.Document import newTempBase

portal =  context.getPortalObject()
portal_diff = portal.portal_diff

# Get the last 2 history of the context
history = context.Base_getZODBChangeHistoryList(context, size=2)

if len(history) > 1:
  # Using this last 2 history dicts, create a Diff
  diff = portal_diff.diffPortalObject(history[1], history[0]).asBeautifiedJSONDiff()
  # Return a list of TempBase objects which can be displayed in a listbox
  tempbase_list = []
  uid = 0
  for x in diff:
    temp_obj = newTempBase(portal,
                          x['path'],
                          **x)
    temp_obj.setUid(int(uid))
    uid = uid + 1
    tempbase_list.append(temp_obj)

  return tempbase_list
