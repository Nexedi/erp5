import json
if REQUEST is None:
  REQUEST = context.REQUEST

# raise ValueError('foo')
document = context.getObject()

subobject_list = document.Base_getRelatedDocumentList()
subobject_result_list = []


for subobject in subobject_list:
  subobject_dict = {}
  subobject_type = subobject.getPortalType()
  subobject_title = subobject.getTitle()

  if subobject_type == 'Sale Supply Line':
    pass
  elif subobject_type == 'Product Individual Variation':
    subobject_dict['title'] = subobject.getTitle()
  elif subobject_title == 'default_image':
    subobject_dict['default_image_url'] = subobject.getPath()
  elif subobject_type == 'Embedded File':
    subobject_dict['image_url'] = subobject.getPath()
  elif subobject_type == 'Purchase Supply Line':
    subobject_dict['price'] = subobject.getBasePrice()
  subobject_result_list.append(subobject_dict)

return json.dumps({
  # 'variation_list': [x[0] for x in document.getVariationCategoryItemList()]
  'related_document_list': subobject_result_list
}, indent=2)
