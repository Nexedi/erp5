## Script (Python) "ProductionOrder_getConsumptionList"
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
result = context.ProductionOrder_zGetMaterialConsumptionList(order_related_movement_uid_list = movement_uid_list)
result += context.ProductionOrder_zGetImmaterialConsumptionList(order_related_movement_uid_list = movement_uid_list)
return result
