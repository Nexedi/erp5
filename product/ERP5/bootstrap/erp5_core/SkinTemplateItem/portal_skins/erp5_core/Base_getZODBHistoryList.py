from AccessControl import getSecurityManager
from zExceptions import Unauthorized
from Products.ERP5Type.Document import newTempBase
portal = context.getPortalObject()
result = []

if not getSecurityManager().getUser().has_permission('View History', context):
  raise Unauthorized()

def beautifyChange(change_dict):
  return ["%s:%s" % (k,change_dict[k]) for k in sorted(change_dict.keys())]

try:
  history_size = portal.portal_preferences.getPreferredHtmlStyleZodbHistorySize()
except AttributeError:
  history_size = 50

for dict_ in context.Base_getZODBChangeHistoryList(context, size=history_size):
  tmp = newTempBase(portal, '')
  dict_['changes'] = beautifyChange(dict_.get('changes', {}))
  tmp.edit(**dict_)
  result.append(tmp)
return result
