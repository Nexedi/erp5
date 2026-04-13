"""
Get any property value, supporting both direct and relation paths.

Args:
  doc: The ERP5 document
  property_path: Property name or relation path (e.g., 'source_section.total_price')
  default: Default value if property not found
"""

from Products.ERP5Type.Utils import convertToUpperCase


# XXX perhaps that's bad
def getRelationProperty(doc, relation_path, default=""):
  parts = relation_path.split('.')
  if len(parts) != 2:
    return default

  relation_name, property_name = parts

  relation_object = None

  try:
    accessor_name = 'get' + convertToUpperCase(relation_name) + 'Value'
    relation_object = getattr(doc, accessor_name)()
  except AttributeError:
    pass

  if relation_object is None:
    try:
      accessor_name = 'get' + relation_name + 'Value'
      relation_object = getattr(doc, accessor_name)()
    except AttributeError:
      pass

  if relation_object is None:
    try:
      accessor_name = 'get' + convertToUpperCase(relation_name)
      relation_object = getattr(doc, accessor_name)()
    except AttributeError:
      pass

  if relation_object is None:
    try:
      getter_name = 'get' + convertToUpperCase(property_name)
      getter = getattr(doc, getter_name)
      value = getter()
      return value if value is not None else default
    except AttributeError:
      return default

  try:
    property_accessor = 'get' + convertToUpperCase(property_name)
    getter = getattr(relation_object, property_accessor)
    value = getter()
    return value if value is not None else default
  except AttributeError:
    value = relation_object.getProperty(property_name, default)
    return value if value is not None else default


if '.' in property_path:
  return getRelationProperty(doc, property_path, default)

# Simple property - try getter first
try:
  getter_name = 'get' + convertToUpperCase(property_path)
  getter = getattr(doc, getter_name)
  value = getter()
  return value if value is not None else default
except AttributeError:
  value = doc.getProperty(property_path, default)
  return value if value is not None else default
