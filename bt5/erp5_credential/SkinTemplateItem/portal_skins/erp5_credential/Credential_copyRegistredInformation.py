"""Copy information from context to an object
Parameters:
destination -- Object where copy property value
mapping -- Define property mapping (List of tuple of 2 property)
copy_none_value -- Copy or not None value of context to destination
erase_empty_value -- Erase or not empty value of destination"""
def getAccessor(prop):
  return "".join([x.capitalize() for x in prop.split('_')])

def copyValue(source_document, source_accessor,
              destination_document, destination_accessor):
  getter = getattr(source_document, 'get%s' % source_accessor)
  value = getter()
  if value is None and copy_none_value or value is not None:
    old_getter = getattr(destination_document, 'get%s' % destination_accessor)
    old_value = old_getter()
    if not old_value and erase_empty_value or old_value:
      setter = getattr(destination_document, 'set%s' % destination_accessor)
      setter(value)

def copyDocument(source_document, destination_document, mapping):
  for source_property, destination_property in mapping:
    source_accessor, destination_accessor = getAccessor(source_property), getAccessor(destination_property)
    copyValue(source_document, source_accessor,
              destination_document, destination_accessor)



copyDocument(context, destination, mapping)
