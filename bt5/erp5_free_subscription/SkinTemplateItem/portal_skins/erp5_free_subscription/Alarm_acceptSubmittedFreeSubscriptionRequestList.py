portal = context.getPortalObject()
portal_preferences = portal.portal_preferences
searchAndActivate_ = portal.portal_catalog.searchAndActivate
def searchAndActivate(**kw):
  searchAndActivate_('FreeSubscriptionRequest_accept', **kw)

portal_type_list = []
if portal_preferences.getPreferredFreeSubscriptionRequestAutomaticApproval():
  portal_type_list.append('Free Subscription Request')

if portal_type_list:
  searchAndActivate(
    portal_type=portal_type_list,
    validation_state='submitted',
  )
