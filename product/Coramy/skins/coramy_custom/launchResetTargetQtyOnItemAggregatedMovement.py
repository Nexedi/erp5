## Script (Python) "launchResetTargetQtyOnItemAggregatedMovement"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
movement_list = context.zGetTissuMovementWithoutItem()
cr = '\n'
tab = '\t'
movement_log = 'Problème'+cr

for movement_item in movement_list :
  movement = movement_item.getObject()
  if movement is not None:
    context.portal_activities.newMessage('SQLDict', movement.getPath(), None, {}, 'Movement_resetTargetQuantity')
    # movement_log.append(movement.getRelativeUrl())

#request.RESPONSE.setHeader('Content-Type','application/text')

return 'fait'
