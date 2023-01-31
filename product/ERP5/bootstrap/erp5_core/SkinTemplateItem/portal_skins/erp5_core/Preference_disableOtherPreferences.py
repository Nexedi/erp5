# When validating a user preference, we invalidate other user preferences.

from Products.ERP5Type.Message import translateString

portal = context.getPortalObject()


if context.getPriority() != 3: # XXX 3 is Priority.USER
  return

for preference in portal.portal_preferences.searchFolder(
    viewable_owner={'query': portal.portal_membership.getAuthenticatedMember().getId(), 'key': 'ExactMatch'},
    portal_type=context.getPortalType()):
  preference = preference.getObject()
  assert portal.portal_membership.getAuthenticatedMember().allowed(preference, ['Owner', ]), preference

  if preference != context and \
      preference.getPreferenceState() == 'enabled' and \
      preference.getPriority() == context.getPriority():
    preference.disable(
      comment=translateString(
        'Automatically disabled when enabling ${preference_title}.',
        mapping={'preference_title': context.getTitle()}))
