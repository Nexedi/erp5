## Script (Python) "getOrderLineModeleOrigine"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
try:
  modele = context.getDefaultValue('resource',portal_type=['Modele'])
  result = modele.getModeleOrigine()
except:
  result = ''

return result
