## Script (Python) "PieceTissu_updateResourceAfterInventory"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
item_list = context.PieceTissu_zGetInventorized()
compteur = 0

for item in item_list :
  compteur+=1
  item_object = item.getObject()
  if item_object is not None:
    movement_list = item_object.getAggregateRelatedValueList()
    if len(movement_list) == 1 :
      movement = movement_list[0]
      item_object.edit(resource_value = movement.getResource(),
                              source_value = movement.getResourceValue().getSource(),
                              variation_category_list = movement.getVariationCategoryList())
#      if movement.getColoris() is not None :
#        print str(item_object.getId())+' : '+str(movement.getResource())+" "+str(movement.getColoris())+" "+str(movement.getResourceValue().getSource())
#      else :
#        print str(item_object.getId())+' : '+str(movement.getResource())+" "+str(movement.getVariante())+" "+str(movement.getResourceValue().getSource())
    else :
      print str(item_object.getId())+' : Problème'
  else :
    print str(item)+' : Problème'

print str(compteur)
return printed
