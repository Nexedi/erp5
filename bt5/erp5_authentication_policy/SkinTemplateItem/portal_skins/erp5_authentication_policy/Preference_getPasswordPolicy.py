# Ideally, we should get those from authentication policy preference
# But how to get meaningfully text for Regular Expression?
document = context.portal_catalog(reference="NXD-Password.Policy", limit=1)
if document:
  return document[0].getTextContent()
return ''
