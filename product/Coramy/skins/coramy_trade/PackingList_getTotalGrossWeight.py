## Script (Python) "PackingList_getTotalGrossWeight"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
packing_list = context
total_gross_weight = 0

container_list = packing_list.contentValues(filter={'portal_type':'Container'})
for container in container_list :
  total_gross_weight += container.getGrossWeight(0)

return total_gross_weight
