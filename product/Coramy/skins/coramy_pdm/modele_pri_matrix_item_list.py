## Script (Python) "modele_pri_matrix_item_list"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=base_category_list=[]
##title=
##
modele = context

first_list = modele.getVariationCategoryItemList(base_category_list=base_category_list)
final_list = []
for list_item in first_list :
  final_list.append((list_item[1],list_item[0]))

if len(final_list)==0 :
  final_list.append((None,None))

return final_list
