## Script (Python) "toto_test"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
print context.variated_reference_matrix_item_list(base_category_list = ('coloris',), base=0)
print context.variated_reference_matrix_item_list(base_category_list = ('taille',), base=0)
print context.variated_reference_matrix_item_list(base_category_list = ('taille','coloris',), base=0, include=0)


print " "
return printed
