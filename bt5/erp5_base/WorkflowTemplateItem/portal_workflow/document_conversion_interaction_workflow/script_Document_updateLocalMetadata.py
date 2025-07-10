document = state_change['object']

if document.getMetaType() == "ERP5 OOo Document":
  document.activate().updateLocalMetadataFromDocument()
else:
  document.updateLocalMetadataFromDocument()
