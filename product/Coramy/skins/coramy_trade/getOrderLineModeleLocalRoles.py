## Script (Python) "getOrderLineModeleLocalRoles"
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
  result = modele.modele_show_local_roles()
except:
  result = ''

return result
