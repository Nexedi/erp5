"""
  Script customized to UNG to don't check the preference permission
"""

if REQUEST is not None:
  from zExceptions import Unauthorized
  raise Unauthorized(script.getId())

portal = context.getPortalObject()

if not context.Person_getUserId():
  # noop in case if invoked on non-user object
  return

from Products.ERP5Type.Message import translateString
preference = portal.portal_preferences.createPreferenceForUser(
                                  context.getReference(), enable=True)

preference.setTitle(translateString('Preference for ${name}',
                     mapping=dict(name=context.getTitle().decode('utf-8'))))

for assignment in context.contentValues(portal_type='Assignment'):
  group = assignment.getGroup(base=True)
  if group:
    preference.setPreferredSectionCategory(group)
    preference.setPreferredAccountingTransactionSectionCategory(group)

return preference
