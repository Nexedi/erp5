document = state_change['object']

if document.getPortalType() in document.getPortalOOoDocumentTypeList():
  document.activate().updateLocalMetadataFromDocument()
else:
  document.updateLocalMetadataFromDocument()
