## Script (Python) "launchTransferVetement"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
item_list = context.zGetVetementList()
cr = '\n'
tab = '\t'

for item_item in item_list :
  item = item_item.getObject()
  if item is not None:
    item.activate().transfer_vetement()

#request.RESPONSE.setHeader('Content-Type','application/text')

return 'lancé'+str(len(item_list))
