## Script (Python) "Resource_getCartesianVariationList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=base_category_list=['coloris','taille','morphologie','variante']
##title=
##
# returns a list of tuples combining possible variations
# we take only into account coloris, taille, variante and morphologie base categories

raw_variation_base_category_list = context.getVariationBaseCategoryList()
variation_base_category_list = []
for base_category in raw_variation_base_category_list :
  if base_category in base_category_list :
    variation_base_category_list.append(base_category)
variation_base_category_list.sort()
variation_list_list = []

for base_category in variation_base_category_list :
  variation_list = map(lambda x:x[1], context.getVariationCategoryItemList(base_category_list=(base_category,)))
  if variation_list != [] :
    variation_list_list.append(variation_list)

cartesian_variation_list = context.cartesianProduct(variation_list_list)
return cartesian_variation_list
