## Script (Python) "launchResetLocationOnLocatedPieceTissu"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
item_list = context.zGetLocatedPieceTissuList()
cr = '\n'
tab = '\t'

for item_item in item_list :
  item = item_item.getObject()
  if item is not None:
    context.portal_activities.newMessage('SQLDict', item.getPath(), None, {}, 'Item_resetLocation')

#request.RESPONSE.setHeader('Content-Type','application/text')

return 'fait'
