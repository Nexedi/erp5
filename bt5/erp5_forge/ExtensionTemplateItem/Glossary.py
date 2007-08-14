def getPropertySheetAttributeList(name):
  from Products.ERP5Type import PropertySheet
  class_ = PropertySheet.__dict__.get(name, None)
  result = []
  for i in getattr(class_, '_properties', ()):
    if 'acquired_property_id' in i:
      continue
    # we want to get only normal property.
    result.append(i['id'])
  return result
