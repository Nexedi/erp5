## Script (Python) "Variated_getTailleClientDict"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# return a dictionary
# key : cartesian_variation_list
# item : taille client

try :
  correspondance = context.getResourceValue().getSpecialiseValue(portal_type=['Correspondance Tailles'])
except :
  correspondance = None

taille_list = context.getTailleList()
cartesian_variation_list = context.Resource_getCartesianVariationList()
taille_client_dict = {}

for variation_list in cartesian_variation_list  :
  mapped_value_list = correspondance.objectValues()
  taille_found = 0
  for mapped_value in mapped_value_list :
    if mapped_value.test(correspondance.asContext(categories=variation_list)) :
      taille_client_dict[str(variation_list)] = mapped_value.getProperty(key='taille_client')
      taille_found =1
      break
  if not taille_found :
    taille_client_dict[str(variation_list)] = ''

return taille_client_dict
