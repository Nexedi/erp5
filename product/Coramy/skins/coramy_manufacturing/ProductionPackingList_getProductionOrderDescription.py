## Script (Python) "ProductionPackingList_getProductionOrderDescription"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
packing_list = context
order = context.getDefaultCausalityValue()
if order is not None :
  return order.getDescription()
else :
  return ''
