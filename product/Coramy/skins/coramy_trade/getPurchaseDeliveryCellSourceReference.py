## Script (Python) "getPurchaseDeliveryCellSourceReference"
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
  variante = cell.getVarianteValue()
except :
  variante = None

if variante is None :
  try :
    variante = cell.getColorisValue()
  except :
    variante = None

if variante is not None and variante.getSourceReference() is not None and variante.getSourceReference() <> '':
  return variante.getSourceReference()
else :
  try :
    resource = cell.getResourceValue()
  except :
    resource = None
  if resource is not None :
    return resource.getSourceReference()
  else :
    return ''
