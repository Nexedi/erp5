## Script (Python) "ProductionOrder_getMaterialSourcingMovementList"
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
return map(lambda o: o.getObject(), context.ProductionOrder_zGetMaterialSourcingMovementList(order_related_movement_uid_list = movement_uid_list))
