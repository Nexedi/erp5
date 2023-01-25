portal = context.getPortalObject()

# make sure cloudoo is available. this check is required ONLY due to
# unit test nature where a bt5 with a data content which is to be reindexed
# is installed BEFORE the real cloudoo is setup in preferences.
if portal.portal_preferences.getPreferredDocumentConversionServerUrl():
  for index_uid in range(len(uid)):
    document_relative_url = getRelativeUrl[index_uid]
    document = portal.restrictedTraverse(document_relative_url)
    if document.Base_isConvertible():
      document.activate(priority=4, tag="conversion").Base_callPreConvert()
