module = context

forbidden_property = ['uid', 'portal_type']
property_list = []

for portal_type in module.allowedContentTypes():
  for property in portal_type.getInstancePropertyAndBaseCategorySet():
    if property not in forbidden_property:
      property_list.append((portal_type.id, property))

property_list.sort()
return [('-- Ignore this Property --', '')] + [(x[1], '%s.%s' % (x[0], x[1])) for x in property_list]
