if object_property_dict['uid'] is None:
  object = None
else:
  object = context.portal_catalog.getObject(object_property_dict['uid'])

if object == None:
  object = context.newContent()

# activity doesn't support security rights yet...
for key in ['uid','id']:
  if key in object_property_dict:
    object_property_dict.pop(key)

object.edit(**object_property_dict)
