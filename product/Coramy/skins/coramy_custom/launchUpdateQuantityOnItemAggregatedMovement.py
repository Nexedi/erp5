## Script (Python) "launchUpdateQuantityOnItemAggregatedMovement"
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
  if movement is not None:
    context.portal_activities.newMessage('SQLDict', movement.getPath(), None, {}, 'updateQuantityOnItemAggregatedMovement')
    # movement_log.append(movement.getRelativeUrl())

request.RESPONSE.setHeader('Content-Type','application/text')

return 'fait'
