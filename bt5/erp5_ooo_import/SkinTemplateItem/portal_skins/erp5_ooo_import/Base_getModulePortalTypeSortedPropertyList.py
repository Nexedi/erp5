module = context

forbidden_property = ['uid', 'portal_type']
property_list = []

for portal_type in module.allowedContentTypes():
  for prop in portal_type.getInstancePropertyAndBaseCategorySet():
    if prop not in forbidden_property:
      property_list.append((portal_type.id, prop))

property_list.sort()
return [
    (x[1], "%s.%s" % (x[0], x[1])) for x in property_list
]
