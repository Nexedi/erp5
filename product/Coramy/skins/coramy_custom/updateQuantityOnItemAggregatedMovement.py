## Script (Python) "updateQuantityOnItemAggregatedMovement"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
movement = context

# initial_qty = movement.getTargetQuantity()

if movement.getPortalType() in ('Inventory Cell', 'Inventory Line') :
  #if movement.getProductionQuantity() != 0.0 :
  #  movement.setProducedItemIdList(movement.getProducedItemIdList())
  #elif movement.getConsumptionQuantity() != 0.0 :
  #  movement.setConsumedItemIdList(movement.getConsumedItemIdList())
  #else : # inventory
  movement.setItemIdList(movement.getItemIdList())
else : # Delivery Line or Cell
  movement.setItemIdList(movement.getItemIdList())

# final_qty = movement.getTargetQuantity()

# return str(initial_qty-final_qty)
