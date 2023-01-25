document = state_change['object']

# calculate new conversion to base_format
document.processFile()

if document.getMetaType() == 'ERP5 OOo Document':
  # XXX How to filter documents which are implementing base_convertable
  # and not text_document
  # Clear base_data
  document.setBaseData(None)
  tag = 'document_%s_convert' % document.getPath()
  document.activate(tag=tag).Document_tryToConvertToBaseFormat()
else:
  # do not run it in activity but not with try except statement
  # Transaction must fail, otherwise data will be lost
  document.convertToBaseFormat()
