## Script (Python) "PieceTissu_resetTargetQuantityOnUnaggregatedMovementList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=delivery_uid
##title=
##
movement_list = context.PieceTissu_zGetUnaggregatedTissuMovementList(uid=delivery_uid)

for movement_item in movement_list :
  movement = movement_item.getObject()
  if movement is not None:
    movement.Movement_resetTargetQuantity()
