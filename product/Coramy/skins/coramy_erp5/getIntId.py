## Script (Python) "getIntId"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
try:
  result = int(context.getId())
except:
  result = 0

return result
