"""
we return only those base categories to which all Document-related portal_types belong
you need to define the list of Document types here
and to add a base category to it in DMSFile property sheets
or manually for all these portal_types
"""

type_list = context.getPortalDocumentTypeList()
nr_of_types = len(type_list)

basecatdict = {}

for type_info in type_list:
  type_base_cat_list = context.portal_types[type_info].getInstanceBaseCategoryList()
  for base_cat in type_base_cat_list:
    basecatdict[base_cat] = basecatdict.setdefault(base_cat, 0)+1

basecatlist = [k for k,v in basecatdict.items() if v == nr_of_types]
basecatlist.sort()
return basecatlist
