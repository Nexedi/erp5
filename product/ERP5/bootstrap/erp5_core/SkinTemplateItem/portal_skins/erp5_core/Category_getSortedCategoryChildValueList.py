from Products.ERP5Type.Log import log
# this script is no longer needed.
log('Category_getSortedCategoryChildValueList', 'use getCategoryChildValueList method')

value_list = filter(lambda o: o.getRelativeUrl() != context.getRelativeUrl(),context.getCategoryChildValueList())
sort_id='int_index'
value_list.sort(key=lambda x: x.getProperty(sort_id))
return value_list
