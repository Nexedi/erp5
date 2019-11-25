from Products.ERP5Type.Log import log
# this script is no longer needed.
log('Category_getSortedCategoryChildValueList', 'use getCategoryChildValueList method')

value_list = [o for o in context.getCategoryChildValueList() if o.getRelativeUrl() != context.getRelativeUrl()]
sort_id='int_index'
value_list.sort(key=lambda x: x.getProperty(sort_id))
return value_list
