"""
  File a password expire event.
"""
from DateTime import DateTime
from Products.ZSQLCatalog.SQLCatalog import Query
from Products.ERP5Type.DateUtils import addToDate

portal = context.getPortalObject()
portal_preferences = portal.portal_preferences

if not portal_preferences.isAuthenticationPolicyEnabled() or \
   not portal.portal_preferences.isPreferredSystemRecoverExpiredPassword():
  # no policy, no sense to file expire at all or symply system do not configured to
  return 0

# Prevent creating new recovery if one was recently created
recovery_list = portal.portal_catalog(
  portal_type="Credential Recovery",
  reference=context.getReference(),
  default_destination_decision_uid=context.getUid(),
  creation_date=Query(range="min", creation_date=addToDate(DateTime(), {'day': -1})),
  limit=1)
if (len(recovery_list) > 0):
  return 0

module = portal.getDefaultModule(portal_type='Credential Recovery')
credential_recovery = module.newContent(
                               portal_type="Credential Recovery",
                               reference=context.getReference(),
                               destination_decision_value=context,
                               language=portal.Localizer.get_selected_language())
context.serialize()
credential_recovery.submit()
