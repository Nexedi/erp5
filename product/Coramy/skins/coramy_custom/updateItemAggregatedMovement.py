## Script (Python) "updateItemAggregatedMovement"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
movement_list = context.zGetItemAggregatedMovement()
cr = '\n'
tab = '\t'
movement_log = 'Problème'+cr

for movement_item in movement_list :
  movement = movement_item.getObject()
  item_list = movement.getAggregateValueList()
  if not item_list in ([], None) :
    quantity = 0
    for item in item_list :
      # verify if resource of item == resource of movement
      if movement.getResource() == item.getResource() :
        # check if variation_category is the same
        if movement.getVariationCategoryList() != item.getVariationCategoryList() :
          movement_log += movement.getRelativeUrl()+tab
          movement_log += str(movement.getVariationCategoryList())+tab
          movement_log += item.getRelativeUrl()+tab
          movement_log += str(item.getVariationCategoryList())+tab+cr
      else :
        movement_log += movement.getRelativeUrl()+tab
        movement_log += str(movement.getVariationCategoryList())+tab
        movement_log += item.getRelativeUrl()+tab
        movement_log += str(item.getVariationCategoryList())+tab+cr

      # verify if quantity of movement == sum (item.getRemainingQuantity)
      quantity += item.getRemainingQuantity()

    if 1 : # movement_MP
      if (movement.getConsumptionQuantity()+movement.getProductionQuantity()) != 0 : # :
        ratio = round(quantity/(movement.getConsumptionQuantity()+movement.getProductionQuantity()),0)
      else :
        ratio = 0
    else : # livraison_fab
      if movement.getTargetQuantity() !=0 :
        ratio = round(quantity/movement.getTargetQuantity(),0)
      else :
        ratio = 0

    if ratio != 1:
      movement_log += movement.getRelativeUrl()+tab
      movement_log += str(movement.getVariationCategoryList())+tab
      #movement_log += str(movement.getTargetQuantity())+tab
      movement_log += str(movement.getConsumptionQuantity()+movement.getProductionQuantity())+tab
      movement_log += str(round(quantity,4))+tab+str(ratio)+cr

request.RESPONSE.setHeader('Content-Type','application/text')

return movement_log
