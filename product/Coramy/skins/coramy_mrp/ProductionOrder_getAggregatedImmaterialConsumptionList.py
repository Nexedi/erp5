## Script (Python) "ProductionOrder_getAggregatedImmaterialConsumptionList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=**kw
##title=
##
movement_list = context.getOrderRelatedMovementList()
movement_uid_list = map(lambda o:o.getUid(), movement_list)
if len(movement_uid_list) > 0 :
  return context.ProductionOrder_zGetAggregatedImmaterialConsumptionList(order_related_movement_uid_list = movement_uid_list)
else :
  return []
