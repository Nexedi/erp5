## Script (Python) "InventoryLine_matrixItemList"
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
    raw_list = context.getResourceValue().getVariationRangeCategoryItemList(base_category, base=0)
    value_list = []
    title_list = []
    for item in raw_list :
      title_list.append(item[0])
      value_list.append(base_category+'/'+item[1])
    for index in range(len(title_list)) :
      clist += [(value_list[index],title_list[index])]
  else :
    title_list = context.getResourceValue().getCategoryMembershipList(base_category, base=0)
    value_list = context.getResourceValue().getCategoryMembershipList(base_category, base=base)
    for  index in range(len(title_list)) :
      clist += [(value_list[index],title_list[index])]

if len(clist)==0 :
  clist.append((None,None))

return clist
