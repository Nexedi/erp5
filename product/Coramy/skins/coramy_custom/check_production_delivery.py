## Script (Python) "check_production_delivery"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
delivery_list = context.object_action_list(selection_name='production_packing_list_selection')

for delivery in delivery_list :
  print '\n'+'Livraison :'+delivery.getId()
  movement_list = delivery.getMovementList()
  for movement in movement_list :
    item_list = movement.getAggregateValueList()
    if not item_list in ([], None) :
      quantity = 0
      for item in item_list :
#        print movement.getResource(),movement.getVariationCategoryList(),item.getResource(),item.getVariationCategoryList()
        # verify if resource of item == resource of movement
        if movement.getResource() == item.getResource() :
          # check if variation_category is the same
          if movement.getVariationCategoryList() != item.getVariationCategoryList() :
            print 'Problème de variante',movement.getVariationCategoryList(),item.getId(),item.getVariationCategoryList()
        else :
          print 'Problème de resource',movement.getResource(),item.getId(),item.getResource()
#      print movement.getResource(), movement.getItemIdList()

        # verify if quantity of movement == sum (item.getRemainingQuantity)
        quantity += item.getRemainingQuantity()

      if quantity != movement.getTargetQuantity() :
        print 'Problème de quantité',movement.getTargetQuantity(),round(quantity,4)

return printed
