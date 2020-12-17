portal = context.getPortalObject()
reference = portal.portal_preferences.getPreferredPasswordPolicyReference()
if reference:
  document = portal.portal_catalog(reference=reference, limit=1)
  if document:
    return document[0].getTextContent()
return ''
