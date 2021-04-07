document = state_change['object']

if document.isSupportBaseDataConversion() and not document.hasBaseData():
  document.processFile()
  document.activate().convertToBaseFormat()
