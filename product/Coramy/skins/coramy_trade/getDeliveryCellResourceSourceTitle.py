## Script (Python) "getDeliveryCellResourceSourceTitle"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
cell = context

try :
  resource = cell.getResourceValue()
except :
  resource = None

if resource is not None :
  try :
    source_title = resource.getDefaultSourceTitle()
  except :
    source_title = ''
else :
  source_title = ''

return source_title
