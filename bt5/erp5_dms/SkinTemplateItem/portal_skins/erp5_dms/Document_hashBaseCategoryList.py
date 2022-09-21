"""
  Used by parellel list field
  Document_library/my_dms_category_list
  (see http://wiki.erp5.org/HowToConfigureParallelListField)
  To produce a tree we use getCategoryChildLogicalPathItemList
  and we cache
"""
from Products.ERP5Type.Cache import CachingMethod

def cached_DMSGetItemList(base_category):
  basecatobject = context.portal_categories.resolveCategory(base_category)
  return basecatobject.getCategoryChildLogicalPathItemList()

cached_DMSGetItemList = CachingMethod(cached_DMSGetItemList, id='DMGetItemListCachedMethodWhatever')

if default_sub_field_property_dict is None:
  default_sub_field_property_dict = {
   'field_type': 'MultiListField',
   'item_list': [],
   'required': 0,
   'value': [],
   'is_right_display': 0,
   'key': 'default',
   'title': 'Categories',
   'size': 5
  }

sub_field_dict = {}

default_sub_field_property_dict['field_type'] = 'ListField'
default_sub_field_property_dict['size'] = 1

for base_category in item_list:
  if base_category not in sub_field_dict:
    basecatobject = context.portal_categories.resolveCategory(base_category)
    sub_field_property_dict = default_sub_field_property_dict.copy()
    sub_field_property_dict['key'] = base_category
    sub_field_property_dict['title'] = basecatobject.getTranslatedTitle()
    # we cache this, so that we can apply expensive path processing techniques
    sub_field_property_dict['item_list'] = cached_DMSGetItemList(base_category)
    sub_field_property_dict['value'] = context.aq_parent.aq_parent.getProperty(base_category)

    sub_field_dict[base_category] = sub_field_property_dict

return sub_field_dict.values()
