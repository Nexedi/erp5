## Script (Python) "modele_print_list"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# Retourne une liste de modèles
# si appelé sur un modèle, la liste contient uniquement le modèle
# si appelé sur le module modèle, la liste contient la sélection de modèles

modele_list = []
request = context.REQUEST
if context.portal_type == 'Modele' :
  modele_list.append(context)
else :
  selection = context.portal_selections.getSelectionFor('modele_selection',REQUEST=context.REQUEST)
  modele_list = map((lambda x:x.getObject()),selection(context=context))

if len(modele_list) > 20 :
  modele_list = modele_list[0:20]

return modele_list
