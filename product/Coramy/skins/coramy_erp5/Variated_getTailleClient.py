## Script (Python) "Variated_getTailleClient"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
cartesian_variation_list = context.Resource_getCartesianVariationList()
taille_client_dict = context.Variated_getTailleClientDict()
taille = context.getTaille()

try :
  taille_client = taille_client_dict[str(cartesian_variation_list[0])]
except :
  taille_items = taille.split('/')
  taille_client = taille_items[len(taille_items)-1]

return taille_client
