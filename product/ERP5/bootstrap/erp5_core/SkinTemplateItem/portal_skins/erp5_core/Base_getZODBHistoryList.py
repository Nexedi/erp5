from AccessControl import getSecurityManager
from zExceptions import Unauthorized
from Products.ERP5Type.Document import newTempBase
portal = context.getPortalObject()
result = []

if not getSecurityManager().getUser().has_permission('View History', context):
  raise Unauthorized()

def beautifyChange(change_dict):
  change_list = []
  for property_name, property_value in sorted(change_dict.items()):
    if isinstance(property_value, basestring):
      try:
        unicode(property_value, 'utf-8')
      except UnicodeDecodeError:
        property_value = '(binary)'
    change_list.append('%s:%s' % (property_name, property_value))
  return change_list

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
