## Script (Python) "ProductionOrder_getTotalDuration"
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
  return context.ProductionOrder_zGetTotalDuration(order_related_movement_uid_list = movement_uid_list)[0].quantity/60
else :
  return 0
