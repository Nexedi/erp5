from zExceptions import Unauthorized
from Products.ERP5Type.Message import translateString
if REQUEST is not None:
  raise Unauthorized(script.getId())

portal = context.getPortalObject()
if not portal.Base_checkPermission('portal_preferences', 'Add portal content'):
  return

try:
  preference = portal.portal_preferences.createPreferenceForUser(
    context.Person_getUserId(),
    enable=True,
  )
except ValueError:
  return

preference.setTitle(translateString('Preference for ${name}',
                     mapping=dict(name=context.getTitle())))

for assignment in context.contentValues(portal_type='Assignment'):
  group = assignment.getGroup(base=True)
  if group:
    preference.setPreferredSectionCategory(group)
    preference.setPreferredAccountingTransactionSectionCategory(group)
  site = assignment.getSite(base=True)
  if site:
    preference.setPreferredNodeCategory(site)

return preference
