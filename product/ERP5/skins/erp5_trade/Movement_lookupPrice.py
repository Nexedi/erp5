## Script (Python) "Movement_lookupPrice"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
resource = context.getResourceValue()
if resource is not None:
  return resource.getSourceBasePrice(0)/resource.getPricedQuantity()
  # return resource.getPrice(context=context) # calls a Resource_lookupPrice itself
else:
  return None
