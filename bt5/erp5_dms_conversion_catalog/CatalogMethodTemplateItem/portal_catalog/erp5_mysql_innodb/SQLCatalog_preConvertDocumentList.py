portal = context.getPortalObject()
MARKER = (None, '',)

address = portal.portal_preferences.getPreferredOoodocServerAddress()
port = portal.portal_preferences.getPreferredOoodocServerPortNumber()
# make sure cloudoo is available. this check is required ONLY due to
# unit test nature where a bt5 with a data content which is to be reindexed 
# is installed BEFORE the real cloudoo is setup in preferences.
if address not in MARKER and port not in MARKER:
  for index_uid in range(len(uid)):
    document_relative_url = getRelativeUrl[index_uid]
    document = portal.restrictedTraverse(document_relative_url)
    if document.Base_isConvertible():
      document.activate(priority=4, tag="conversion").Base_callPreConvert()
