## Script (Python) "launchSetStopDateONProdDelivery"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
packing_list = context.zGetProductionDeliveryList()
cr = '\n'
tab = '\t'

for packing_item in packing_list :
  packing = packing_item.getObject()
  if packing is not None:
    packing.activate().recursiveImmediateReindexObject()

return 'lancé'
