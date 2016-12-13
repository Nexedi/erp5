portal = context.getPortalObject()
if portal.portal_preferences.getPreferredFreeSubscriptionRequestAutomaticApproval():
  portal.portal_catalog.searchAndActivate(
    'FreeSubscriptionRequest_accept',
    portal_type='Free Subscription Request',
    validation_state='submitted',
  )
