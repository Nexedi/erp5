## Script (Python) "goTest"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
#return context.setVariationBaseCategoryList
context.setVariationBaseCategoryList(('coloris'))
return  context.getVariationBaseCategoryList(), context.variation_base_category_list
