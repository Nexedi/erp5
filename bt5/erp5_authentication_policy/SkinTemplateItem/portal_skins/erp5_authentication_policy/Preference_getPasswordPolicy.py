portal = context.getPortalObject()
reference = portal.portal_preferences.getPreferredPasswordPolicyReference()
if reference:
  document = portal.portal_catalog.getDocumentValueList(
    portal_type="Web Page",
    validation_state=["released", "published_alive", "published"],
    reference=reference,
    limit=1)
  if document:
    return document[0].getTextContent()
return ''
