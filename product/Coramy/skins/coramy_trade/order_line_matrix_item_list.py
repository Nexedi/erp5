## Script (Python) "order_line_matrix_item_list"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=base_category_list=[], base=1, include=1
##title=
##
clist = []
variation_category_list=[]

if include == 1 :
  for category in context.getVariationBaseCategoryList():
    if category in base_category_list :
      variation_category_list.append(category)
else :
  for category in context.getVariationBaseCategoryList():
    if not category in base_category_list :
      variation_category_list.append(category)

for base_category in variation_category_list :
    if base_category in ('coloris','morphologie','variante'):
      title_list = map(lambda x:('/'.join(x.getPhysicalPath()[len(x.portal_categories.getPhysicalPath()):])),
         context.getValueList(base_category))
      value_list = context.getCategoryMembershipList(base_category, base=base)
      for index in range(len(title_list)) :
        clist += [(value_list[index],title_list[index])]
    else :
      title_list = context.getCategoryMembershipList(base_category, base=0)
      value_list = context.getCategoryMembershipList(base_category, base=base)
      for  index in range(len(title_list)) :
        clist += [(value_list[index],title_list[index])]

if len(clist)==0 :
  clist.append((None,None))

return clist
