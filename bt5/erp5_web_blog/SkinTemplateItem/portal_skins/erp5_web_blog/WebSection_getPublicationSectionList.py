'''
  Return the list of publication_section used in the predicate.
'''
publication_section_list=[]
if 'publication_section' not in context.getMembershipCriterionBaseCategoryList():
  return publication_section_list
for category in context.getMembershipCriterionCategoryList():
  base_category, category_id = category.split('/', 1)
  if base_category == 'publication_section':
    publication_section_list.append(category_id)
return publication_section_list
