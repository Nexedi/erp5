"""
  File a failed authentication attempt.
"""
portal = context.getPortalObject()
portal_preferences = portal.portal_preferences

if not portal_preferences.isAuthenticationPolicyEnabled():
  # no policy, no sense to file failure
  return 0

activate_kw = {'tag': 'authentication_event_%s' %context.getReference()}
authentication_event = portal.system_event_module.newContent(
                                                    portal_type = "Authentication Event",
                                                    activate_kw = activate_kw)
authentication_event.setDestinationValue(context)
authentication_event.confirm()
return authentication_event
