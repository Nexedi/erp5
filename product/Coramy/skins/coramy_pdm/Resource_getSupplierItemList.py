## Script (Python) "Resource_getSupplierItemList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# returns a list of all suppliers in relation source
# with resources with a given portal_type

supplier_list = context.Resource_sqlSupplierSearch(portal_type_list = ('Tissu', 'Composant'))

supplier_item_list = []
sorted_supplier_title_list = []
for supplier in supplier_list :
  sorted_supplier_title_list.append(supplier.title)
sorted_supplier_title_list.sort()

supplier_item_list = map(lambda x:(x,x),sorted_supplier_title_list)

return supplier_item_list
