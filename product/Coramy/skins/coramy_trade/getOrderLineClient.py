## Script (Python) "getOrderLineClient"
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
  result = order.getDefaultValue('destination',portal_type=['Organisation']).getTitle()
except:
  result = ''

return result
