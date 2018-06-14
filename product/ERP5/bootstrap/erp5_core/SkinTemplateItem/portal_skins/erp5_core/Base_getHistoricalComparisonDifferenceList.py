from Products.PythonScripts.standard import Object
from Products.ERP5Type.Log import log
from Products.ERP5Type.Document import newTempBase
from ZODB.POSException import ConflictError
from zExceptions import Unauthorized
Base_translateString = context.Base_translateString

portal =  context.getPortalObject()
portal_diff = portal.portal_diff
try:
  context.HistoricalRevisions[serial]
except (ConflictError, Unauthorized):
  raise
except Exception:# POSKeyError
  return [newTempBase(portal, Base_translateString('Historical revisions are'
                      ' not available, maybe the database has been packed'))]

if next_serial == '0.0.0.0':
  # In case the next serial is 0.0.0.0, we should always be considering the
  # new object as the current context
  new_getProperty = context.getProperty
  new = context
else:
  new = context.HistoricalRevisions[next_serial]
  new_getProperty = new.getProperty
old = context.HistoricalRevisions[serial]
result = []

binary_data_explanation = Base_translateString("Binary data can't be displayed")
base_error_message = Base_translateString('(value retrieval failed)')

# XXX: Instead of creating a separate property list here, we can use DiffTool
# to directky find out the beautified diff and send it to the listbox

diff = portal_diff.diffPortalObject(old, new).asBeautifiedJSONDiff()

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
