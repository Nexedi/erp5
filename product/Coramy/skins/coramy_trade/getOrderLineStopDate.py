## Script (Python) "getOrderLineStopDate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
try:
  order = context.aq_parent
  result = order.getStopDate()
except:
  result = ''

return result
